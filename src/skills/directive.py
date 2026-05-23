from dataclasses import dataclass, field


@dataclass
class SkillDirective:
    objective: str
    use_cases: list[str] = field(default_factory=list)
    avoid_when: list[str] = field(default_factory=list)
    execution_flow: list[str] = field(default_factory=list)

    def compile_instructions(self) -> str:
        sections = [self.objective]

        if self.use_cases:
            sections.append(f"USE: {' | '.join(self.use_cases)}")

        if self.avoid_when:
            sections.append(f"AVOID: {' | '.join(self.avoid_when)}")

        if self.execution_flow:
            sections.append(f"FLOW: {' -> '.join(self.execution_flow)}")

        return "\n".join(sections)
