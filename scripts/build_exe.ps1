param(
    [ValidateSet("all", "en-us", "pt-br")]
    [string]$Variant = "all"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OpenWakeWordModelRoot = Join-Path $ProjectRoot "src\resources\models\openwakeword"
$VoskModelRoot = Join-Path $ProjectRoot "src\resources\models\vosk"
$PackagingEnvRoot = Join-Path $ProjectRoot "packaging\env"
$env:UV_CACHE_DIR = Join-Path $ProjectRoot ".tmp_uv_cache"

$CommonArgs = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onefile",
    "--paths", ".",
    "--additional-hooks-dir", "packaging/hooks",
    "--collect-binaries", "vosk",
    "--collect-data", "vosk",
    "--add-data", "$OpenWakeWordModelRoot\hey_keeper_v2.onnx;src/resources/models/openwakeword",
    "--add-data", "$OpenWakeWordModelRoot\melspectrogram.onnx;src/resources/models/openwakeword",
    "--add-data", "$OpenWakeWordModelRoot\embedding_model.onnx;src/resources/models/openwakeword",
    "--exclude-module", "src.cli",
    "--exclude-module", "tests",
    "--exclude-module", "pytest",
    "--exclude-module", "faker",
    "--exclude-module", "PyInstaller",
    "--exclude-module", "sklearn.datasets",
    "--exclude-module", "sklearn.datasets.tests",
    "--exclude-module", "sklearn.tests",
    "--exclude-module", "scipy.datasets",
    "--exclude-module", "scipy._lib.tests",
    "--distpath", "dist",
    "--workpath", ".tmp_pyinstaller/build",
    "--specpath", ".tmp_pyinstaller"
)

$BuildVariants = @(
    @{
        Id = "en-us"
        Name = "KeepClicking-en-us"
        VoskModelDir = "vosk-model-small-en-us-0.15"
        BundledEnvPath = (Join-Path $PackagingEnvRoot "en-us\packaged.env")
    },
    @{
        Id = "pt-br"
        Name = "KeepClicking-pt-br"
        VoskModelDir = "vosk-model-small-pt-0.3"
        BundledEnvPath = (Join-Path $PackagingEnvRoot "pt-br\packaged.env")
    }
)

if ($Variant -ne "all") {
    $BuildVariants = @($BuildVariants | Where-Object { $_.Id -eq $Variant })
}

foreach ($BuildVariant in $BuildVariants) {
    $variantName = $BuildVariant.Name
    $variantVoskModelDir = $BuildVariant.VoskModelDir
    $bundledEnvPath = $BuildVariant.BundledEnvPath
    $voskModelPath = Join-Path $VoskModelRoot $variantVoskModelDir

    if (-not (Test-Path -LiteralPath $bundledEnvPath)) {
        throw "Bundled env file not found: $bundledEnvPath"
    }

    if (-not (Test-Path -LiteralPath $voskModelPath)) {
        throw "Bundled Vosk model not found: $voskModelPath"
    }

    Write-Host "Building $variantName..."
    & uv run pyinstaller @CommonArgs `
        --name $variantName `
        --add-data "$bundledEnvPath;." `
        --add-data "$voskModelPath;src/resources/models/vosk/$variantVoskModelDir" `
        "src/main.py"

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed for $variantName with exit code $LASTEXITCODE."
    }
}
