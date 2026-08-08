from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_packaged_env_variants_point_to_matching_vosk_models():
    en_us_env = (
        PROJECT_ROOT / "packaging" / "env" / "en-us" / "packaged.env"
    ).read_text(encoding="utf-8")
    pt_br_env = (
        PROJECT_ROOT / "packaging" / "env" / "pt-br" / "packaged.env"
    ).read_text(encoding="utf-8")

    assert "speech_language=en_us" in en_us_env
    assert "offline_model_path=src/resources/models/vosk/vosk-model-small-en-us-0.15" in en_us_env
    assert "speech_language=pt_br" in pt_br_env
    assert "offline_model_path=src/resources/models/vosk/vosk-model-small-pt-0.3" in pt_br_env


def test_build_script_variants_bundle_matching_vosk_models():
    build_script = (PROJECT_ROOT / "scripts" / "build_exe.ps1").read_text(
        encoding="utf-8"
    )

    assert 'Name = "KeepClicking-en-us"' in build_script
    assert 'VoskModelDir = "vosk-model-small-en-us-0.15"' in build_script
    assert 'Name = "KeepClicking-pt-br"' in build_script
    assert 'VoskModelDir = "vosk-model-small-pt-0.3"' in build_script
