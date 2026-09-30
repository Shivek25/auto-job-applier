# src/resume/compiler.py
import json
import shutil
from pathlib import Path
import typst
from src.resume.models import MasterProfile

class ResumeCompiler:
    def __init__(self, template_path: Path | str = "templates/modern_ats.typ"):
        self.template_path = Path(template_path).resolve()

    def compile_pdf(self, profile: MasterProfile, output_pdf_path: Path | str) -> Path:
        out_pdf = Path(output_pdf_path).resolve()
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = out_pdf.parent / f"tmp_{out_pdf.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Write profile data JSON to temp dir
            json_file = temp_dir / "profile_data.json"
            with open(json_file, "w", encoding="utf-8") as f:
                f.write(profile.model_dump_json(indent=2))
            
            # Copy typst template to temp dir
            typ_file = temp_dir / "resume.typ"
            shutil.copyfile(self.template_path, typ_file)
            
            # Compile via typst python package
            typst.compile(str(typ_file), output=str(out_pdf))
            
            if not out_pdf.exists():
                raise RuntimeError(f"Typst compilation failed to generate PDF at {out_pdf}")
            return out_pdf
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
