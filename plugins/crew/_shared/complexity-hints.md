# Complexity-Adaptive Behavior

Agents self-assess task complexity and adjust their depth accordingly.
Claude Code handles model selection - agents do NOT control which model runs.

## Complexity Assessment

Each agent evaluates the task and adjusts behavior:

| Signal | Low (<=0.3) | Medium (0.3-0.7) | High (>0.7) |
|--------|-----------|-------------------|-------------|
| Files affected | 1-2 | 3-10 | 10+ |
| Dependencies | None | Some | Cross-module |
| Security | None | Standard | Critical |
| Architecture | None | Local | System-wide |

## Behavioral Adaptation

### Low Complexity
- Direct implementation, minimal exploration
- Skip extensive analysis
- Fast iteration, quick verification

### Medium Complexity
- Standard TDD workflow
- Appropriate context gathering
- Pattern-following implementation

### High Complexity
- Comprehensive exploration and analysis
- Deep dependency/impact analysis
- Serena symbol-based exploration
- Lessons learned check (MEMORY.md, Serena)
- Multiple alternatives considered

## Integration
Each agent has a "Complexity-Adaptive Behavior" section documenting specific adaptations.
