Add-Type -Path 'C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\Microsoft.AnalysisServices.Tabular.dll'

$json = [System.IO.File]::ReadAllText("powerbi\clean_model.bim")
Write-Output "Deserializing model..."
$db = [Microsoft.AnalysisServices.Tabular.JsonSerializer]::DeserializeDatabase($json)

$targetModelDir = "powerbi\Veyra_Ecommerce_Analytics.SemanticModel"
$definitionDir = Join-Path $targetModelDir "definition"

if (Test-Path $definitionDir) {
    Remove-Item -Path $definitionDir -Recurse -Force
}
New-Item -ItemType Directory -Path $definitionDir | Out-Null

Write-Output "Serializing model to TMDL at $definitionDir..."
[Microsoft.AnalysisServices.Tabular.TmdlSerializer]::SerializeModelToFolder($db.Model, $definitionDir)
Write-Output "TMDL serialization complete!"

# Write definition.pbism
$pbismContent = @{
    version = "4.0"
} | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText((Join-Path $targetModelDir "definition.pbism"), $pbismContent, [System.Text.Encoding]::UTF8)
Write-Output "definition.pbism updated to version 4.0"

# Backup model.bim
$modelBimPath = Join-Path $targetModelDir "model.bim"
if (Test-Path $modelBimPath) {
    Copy-Item -Path $modelBimPath -Destination (Join-Path $targetModelDir "model.bim.bak") -Force
    Remove-Item -Path $modelBimPath -Force
    Write-Output "model.bim backed up to model.bim.bak and removed from root of SemanticModel"
}

# Clean up test folders
if (Test-Path "powerbi\test_tmdl") { Remove-Item -Path "powerbi\test_tmdl" -Recurse -Force }
if (Test-Path "powerbi\test_tmdl_db") { Remove-Item -Path "powerbi\test_tmdl_db" -Recurse -Force }

Write-Output "Done! Listing SemanticModel structure:"
Get-ChildItem -Path $targetModelDir -Recurse | Select-Object FullName, Length
