# Starts the project's local MongoDB (replica set rs0) on 127.0.0.1:27017.
# Data is stored in <project>\mongodb-data. Keep this window open while working.

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "mongodb-data"

$Mongod = Get-ChildItem "C:\Program Files\MongoDB\Server\*\bin\mongod.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if (-not $Mongod) {
    throw "mongod.exe not found. Install MongoDB Community Server first (see README.md)."
}

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

& $Mongod.FullName --replSet rs0 --port 27017 --bind_ip 127.0.0.1 --dbpath $DataDir
