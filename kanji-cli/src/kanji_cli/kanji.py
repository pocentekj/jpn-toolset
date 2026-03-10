from dataclasses import dataclass
import orjson


@dataclass
class Kanji:
    kanji: str
    meaning: str | None
    on_readings: str | None
    on_readings_norm: str | None
    kun_readings: str | None
    name_readings: str | None
    components: str | None
    freq: int

    def format_pretty(self) -> str:
        lines: list[str] = []

        leader = f"{self.kanji}"
        if self.meaning:
            leader += f" means '{self.meaning}'"
        lines.append(leader)
        lines.append("")

        # "dict" type display - do not show normalized on readings
        for reading in ("on_readings", "kun_readings", "name_readings"):
            prefix = reading.split("_")[0]
            value = getattr(self, reading, None)
            if value is not None:
                lines.append(f"{prefix}: {value}")
        lines.append("")

        if self.components:
            lines.append(f"Components: {self.components}")

        return "\n".join(lines).rstrip() + "\n"

    def format_markdown(self) -> str:
        head = f"### {self.kanji}"
        if self.meaning:
            head += f" means '{self.meaning}'\n\n"

        table = (
            "| | Reading |\n"
            "| ----------- | ----------- |\n"
            f"on | {self.on_readings} |\n"
            f"kun | {self.kun_readings} |\n\n"
        )

        comp = ""
        if self.components:
            comp = f"Components: {self.components}\n"

        return head + table + comp

    def to_storage_dict(self) -> dict:
        as_dict = {
            "kanji": self.kanji,
            "on": self.on_readings,
            "kun": self.kun_readings,
            "components": self.components,
            "meanings": [],
        }

        if self.meaning:
            as_dict["meanings"] = self.meaning.split("; ")

        return as_dict

    def format_json(self) -> str:
        return orjson.dumps(self.to_storage_dict()).decode("utf-8")
