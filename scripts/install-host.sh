#!/usr/bin/env bash
# 把本仓库这份 SKILL.md 软链到各 Agent 的 skills 目录。
# 不复制、不改正文。一份 Skill，多宿主发现。
set -euo pipefail

SKILL_SLUG="pangu-distill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'EOF'
用法:
  bash scripts/install-host.sh                  # 用户级：agents + claude + codex
  bash scripts/install-host.sh --host all       # 用户级：全部已知宿主
  bash scripts/install-host.sh --host cursor --project
  bash scripts/install-host.sh --project        # 当前目录：.agents/skills/pangu-distill
  bash scripts/install-host.sh --list
  bash scripts/install-host.sh --uninstall --host claude

选项:
  --host NAME     agents|claude|codex|cursor|openclaw|gemini|copilot|hermes|opencode|all
                  可重复。默认用户级：agents,claude,codex
  --project       安装到当前目录的项目级 skills（cursor 只支持项目级）
  --project-dir D 项目根，默认 $PWD
  --uninstall     只删除指向本仓库的软链
  --force         覆盖已存在的非本仓库软链/目录
  --list          打印目标路径，不安装
  -h, --help
EOF
}

HOSTS=()
DO_PROJECT=0
PROJECT_DIR="${PWD}"
UNINSTALL=0
FORCE=0
LIST_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOSTS+=("$2")
      shift 2
      ;;
    --project)
      DO_PROJECT=1
      shift
      ;;
    --project-dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    --uninstall)
      UNINSTALL=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --list)
      LIST_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 2
      ;;
  esac
done

user_dir_for() {
  case "$1" in
    agents) echo "${HOME}/.agents/skills/${SKILL_SLUG}" ;;
    claude) echo "${HOME}/.claude/skills/${SKILL_SLUG}" ;;
    codex) echo "${HOME}/.codex/skills/${SKILL_SLUG}" ;;
    openclaw) echo "${HOME}/.openclaw/skills/${SKILL_SLUG}" ;;
    gemini) echo "${HOME}/.gemini/skills/${SKILL_SLUG}" ;;
    copilot) echo "${HOME}/.config/github-copilot/skills/${SKILL_SLUG}" ;;
    hermes) echo "${HOME}/.hermes/skills/${SKILL_SLUG}" ;;
    opencode) echo "${HOME}/.config/opencode/skills/${SKILL_SLUG}" ;;
    cursor)
      echo "" # 用户级不支持
      ;;
    *)
      echo "未知宿主: $1" >&2
      return 1
      ;;
  esac
}

project_dir_for() {
  local root="$1"
  case "$2" in
    agents) echo "${root}/.agents/skills/${SKILL_SLUG}" ;;
    cursor) echo "${root}/.cursor/skills/${SKILL_SLUG}" ;;
    claude) echo "${root}/.claude/skills/${SKILL_SLUG}" ;;
    codex) echo "${root}/.codex/skills/${SKILL_SLUG}" ;;
    copilot) echo "${root}/.github/skills/${SKILL_SLUG}" ;;
    openclaw) echo "${root}/skills/${SKILL_SLUG}" ;;
    *)
      echo "项目级不支持宿主: $2" >&2
      return 1
      ;;
  esac
}

if [[ ${#HOSTS[@]} -eq 0 ]]; then
  if [[ "${DO_PROJECT}" -eq 1 ]]; then
    HOSTS=(agents)
  else
    HOSTS=(agents claude codex)
  fi
fi

if [[ " ${HOSTS[*]} " == *" all "* ]]; then
  if [[ "${DO_PROJECT}" -eq 1 ]]; then
    HOSTS=(agents cursor claude codex copilot openclaw)
  else
    HOSTS=(agents claude codex openclaw gemini copilot hermes opencode)
  fi
fi

TARGETS=()
for host in "${HOSTS[@]}"; do
  if [[ "${DO_PROJECT}" -eq 1 ]]; then
    if [[ "${host}" == "gemini" || "${host}" == "hermes" || "${host}" == "opencode" ]]; then
      echo "跳过 ${host}：无常规项目级目录，改用 --host ${host} 做用户级安装" >&2
      continue
    fi
    TARGETS+=("$(project_dir_for "${PROJECT_DIR}" "${host}")")
  else
    if [[ "${host}" == "cursor" ]]; then
      echo "Cursor 没有用户级 skills 目录，改用: --host cursor --project" >&2
      continue
    fi
    TARGETS+=("$(user_dir_for "${host}")")
  fi
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "没有可安装的目标。" >&2
  exit 1
fi

if [[ "${LIST_ONLY}" -eq 1 ]]; then
  printf '%s\n' "${TARGETS[@]}"
  exit 0
fi

link_one() {
  local dest="$1"
  local dest_dir
  dest_dir="$(dirname "${dest}")"

  if [[ "${dest}" == "${REPO_ROOT}" ]]; then
    echo "跳过 ${dest}：目标就是本仓库根目录"
    return 0
  fi

  if [[ -e "${dest}" || -L "${dest}" ]]; then
    if [[ -L "${dest}" ]]; then
      local current
      current="$(readlink "${dest}")"
      if [[ "${current}" == "${REPO_ROOT}" ]]; then
        if [[ "${UNINSTALL}" -eq 1 ]]; then
          rm "${dest}"
          echo "已移除 ${dest}"
        else
          echo "已存在 ${dest}"
        fi
        return 0
      fi
    fi
    if [[ "${UNINSTALL}" -eq 1 ]]; then
      echo "跳过 ${dest}：不是指向本仓库的软链"
      return 0
    fi
    if [[ "${FORCE}" -eq 1 ]]; then
      rm -rf "${dest}"
    else
      echo "已存在且不是本仓库软链: ${dest}（加 --force 覆盖）" >&2
      return 1
    fi
  fi

  if [[ "${UNINSTALL}" -eq 1 ]]; then
    echo "不存在 ${dest}"
    return 0
  fi

  mkdir -p "${dest_dir}"
  ln -sfn "${REPO_ROOT}" "${dest}"
  echo "已链接 ${dest} -> ${REPO_ROOT}"
}

status=0
for dest in "${TARGETS[@]}"; do
  if ! link_one "${dest}"; then
    status=1
  fi
done

if [[ "${UNINSTALL}" -eq 0 && "${status}" -eq 0 ]]; then
  echo
  echo "装好后重启或重新扫描 Agent。在对话里说：蒸馏「长期主义」"
fi

exit "${status}"
