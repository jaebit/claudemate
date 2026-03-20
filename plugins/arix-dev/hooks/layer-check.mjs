#!/usr/bin/env node

// PreToolUse hook: Write|Edit 시 .cs/.csproj 파일의 레이어 정보를 표시
// _shared/arix-rules.md §3 참조 규칙 안내

const toolInput = process.env.TOOL_INPUT;
if (!toolInput) {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

const filePath = JSON.parse(toolInput).file_path || "";

if (!filePath.endsWith(".cs") && !filePath.endsWith(".csproj")) {
  console.log(JSON.stringify({ result: "continue" }));
  process.exit(0);
}

const layers = {
  BuildingBlocks: "Cross-cutting",
  Registry: "L2 Discovery",
  Execution: "L3 Execution",
  Gateway: "L4 Capability Gateway",
  Knowledge: "L6 Knowledge",
  Governance: "L5 Governance",
  Hosts: "Deploy Host",
};

const match = filePath.match(/Arix\.([A-Za-z]+)\./);
if (match) {
  const layer = layers[match[1]] || "Unknown";
  console.log(
    JSON.stringify({
      result: "continue",
      message: `[arix-dev] Layer: ${layer} | 참조 규칙: _shared/arix-rules.md §3 참조`,
    })
  );
} else {
  console.log(JSON.stringify({ result: "continue" }));
}
