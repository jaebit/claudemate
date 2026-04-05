# 도메인 지식 목차

에이전트가 도메인 지식을 빠르게 탐색하기 위한 목차입니다.

## 프로젝트 개요

- 프로젝트명: claudemate
- 설명: Claude Code 플러그인 마켓플레이스 — 플러그인, 스킬, 에이전트, MCP 서버를 관리하는 오케스트레이터
- 기술 스택: Node.js, Python 3, Bash, YAML, Markdown
- 주요 언어: JavaScript (MCP 서버/훅), Python (crew 테스트/훅), Shell

## 핵심 개념

- **Plugin**: `.claude-plugin/` 디렉토리 구조. `plugin.json` + commands/skills/agents/hooks 자동 발견
- **Marketplace**: `.claude-plugin/marketplace.json` — 모든 플러그인 등록 레지스트리
- **Skill**: `skills/*/SKILL.md` — 재사용 가능한 절차적 지식
- **Hook**: `hooks/hooks.json` — PreToolUse/PostToolUse/Stop/SubagentStop 이벤트 핸들러
- **MCP Server**: `plugin.json`의 `mcpServers` 필드로 등록

## 플러그인 구조 규칙 (불변)

- `plugin.json` 허용 필드: `name`, `version`, `description`, `mcpServers`만
- 파일 기반 자동 발견: commands, agents, skills, hooks는 경로로 자동 등록
- 모든 플러그인은 `marketplace.json`에 반드시 등록

## 활성 플러그인

- `plugins/crew/` — 자율 개발 오케스트레이터 (Python, pytest)
- `plugins/gemini-cli/` — Gemini CLI 통합
- `plugins/worktree/` — Git worktree 관리 (3 skills: create, merge, cleanup)
- `plugins/autohone/` — Self-Improving Harness
- `plugins/arch-guard/` — 아키텍처 가드
- `plugins/autopilot/` — 자율 실행 파이프라인
- `plugins/multi-model-debate/` — 다중 모델 토론

## 문서 위치

- 아키텍처: `domain/knowledge-base/architecture/`
- API 명세: `domain/knowledge-base/api-specs/`
- 코딩 표준: `domain/knowledge-base/coding-standards/`
- 비즈니스 규칙: `domain/knowledge-base/business-rules/`

## 불변 규칙 (domain/rules/)

- `security.yaml` — 보안 불변 규칙
- `coding.yaml` — 코딩 불변 규칙
- `ai-agent-safety.yaml` — AI 에이전트 안전 규칙
