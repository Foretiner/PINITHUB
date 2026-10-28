$ErrorActionPreference = 'Stop'

$modelDirectory = Join-Path $PSScriptRoot 'models'
New-Item -ItemType Directory -Force -Path $modelDirectory | Out-Null

# Research-only pretrained detector and ArcFace embedding model. The official
# InsightFace model zoo restricts its pretrained packs to non-commercial research.
$buffaloArchive = Join-Path $modelDirectory 'buffalo_l.zip'
$buffaloUrl = 'https://github.com/deepinsight/insightface/releases/download/model-zoo/buffalo_l.zip'
$buffaloSha256 = '80FFE37D8A5940D59A7384C201A2A38D4741F2F3C51EEF46EBB28218A7B0CA2F'
$buffaloModels = @(
    @{ Name = 'det_10g.onnx'; Hash = '5838F7FE053675B1C7A08B633DF49E7AF5495CEE0493C7DCF6697200B85B5B91' },
    @{ Name = 'w600k_r50.onnx'; Hash = '4C06341C33C2CA1F86781DAB0E829F88AD5B64BE9FBA56E56BC9EBDEFC619E43' }
)
$needBuffaloArchive = $false
foreach ($model in $buffaloModels) {
    $existing = Join-Path $modelDirectory $model.Name
    if (-not (Test-Path -LiteralPath $existing) -or (Get-FileHash -LiteralPath $existing -Algorithm SHA256).Hash -ne $model.Hash) {
        $needBuffaloArchive = $true
    }
}
if ($needBuffaloArchive) {
    if (-not (Test-Path -LiteralPath $buffaloArchive)) {
        Invoke-WebRequest -Uri $buffaloUrl -OutFile $buffaloArchive
    }
    $actualArchiveHash = (Get-FileHash -LiteralPath $buffaloArchive -Algorithm SHA256).Hash
    if ($actualArchiveHash -ne $buffaloSha256) {
        Remove-Item -LiteralPath $buffaloArchive -Force
        throw 'InsightFace buffalo_l archive checksum mismatch; removed the file.'
    }
}
foreach ($model in $buffaloModels) {
    $destination = Join-Path $modelDirectory $model.Name
    if (-not (Test-Path -LiteralPath $destination) -or (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ne $model.Hash) {
        Expand-Archive -LiteralPath $buffaloArchive -DestinationPath $modelDirectory -Force
    }
    $actualHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if ($actualHash -ne $model.Hash) {
        Remove-Item -LiteralPath $destination -Force
        throw "Checksum mismatch for $($model.Name); removed the file."
    }
    Write-Host "$($model.Name): checksum verified (non-commercial research only)"
}
if (Test-Path -LiteralPath $buffaloArchive) { Remove-Item -LiteralPath $buffaloArchive -Force }

$assets = @(
    @{
        Name = 'anti-spoof-mn3.onnx'
        Url = 'https://storage.openvinotoolkit.org/repositories/open_model_zoo/public/2022.1/anti-spoof-mn3/anti-spoof-mn3.onnx'
        Algorithm = 'SHA384'
        Hash = '6DE4534964B723397B3E8C995CADCF43BC007CC2F9930B95AE25F76ADCCECE5D1D4D058D0B15117B9E4A9F758424F92A'
    },
    @{
        Name = 'face_landmarker.task'
        Url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
        Algorithm = 'SHA256'
        Hash = '64184E229B263107BC2B804C6625DB1341FF2BB731874B0BCC2FE6544E0BC9FF'
    }
)

foreach ($asset in $assets) {
    $destination = Join-Path $modelDirectory $asset.Name
    $temporary = "$destination.download"
    if (-not (Test-Path -LiteralPath $destination)) {
        Invoke-WebRequest -Uri $asset.Url -OutFile $temporary
        Move-Item -LiteralPath $temporary -Destination $destination -Force
    }
    $actualHash = (Get-FileHash -LiteralPath $destination -Algorithm $asset.Algorithm).Hash
    if ($actualHash -ne $asset.Hash) {
        Remove-Item -LiteralPath $destination -Force
        throw "Checksum mismatch for $($asset.Name); removed the file. Re-run this script to download it again."
    }
    Write-Host "$($asset.Name): checksum verified"
}
