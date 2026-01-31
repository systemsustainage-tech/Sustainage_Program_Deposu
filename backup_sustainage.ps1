param(
    [string]$RemoteHost = "72.62.150.207",
    [string]$RemoteUser = "root",
    [string]$RemoteDir = "/var/www/sustainage",
    [string]$BackupRoot = "D:\SUSTAINAGE\YEDEK",
    [string]$LocalSource = "C:\SUSTAINAGESERVER",
    [switch]$LocalOnly,
    [switch]$RemoteOnly
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

$localBackupDir = Join-Path $BackupRoot "local"
$remoteBackupDir = Join-Path $BackupRoot "remote"

New-Item -ItemType Directory -Force -Path $localBackupDir | Out-Null
New-Item -ItemType Directory -Force -Path $remoteBackupDir | Out-Null

if (-not $RemoteOnly) {
    $localArchive = Join-Path $localBackupDir "sustainage_local_$timestamp.zip"
    if (Test-Path $localArchive) { Remove-Item $localArchive -Force }
    Compress-Archive -Path (Join-Path $LocalSource "*") -DestinationPath $localArchive
}

if (-not $LocalOnly) {
    $remoteArchiveName = "sustainage_remote_$timestamp.tar.gz"
    $remoteArchivePath = "/tmp/$remoteArchiveName"
    $sshTarget = "$RemoteUser@$RemoteHost"

    $remoteDirTrimmed = $RemoteDir.TrimEnd('/')
    $remoteParts = $remoteDirTrimmed -split '/'
    $remoteFolderName = $remoteParts[-1]
    $remoteParent = ($remoteParts[0..($remoteParts.Length - 2)] -join '/')
    if (-not $remoteParent) { $remoteParent = "/" }

    $createCmd = "cd $remoteParent && tar czf $remoteArchivePath $remoteFolderName"
    ssh $sshTarget $createCmd

    $localRemoteArchive = Join-Path $remoteBackupDir $remoteArchiveName
    if (Test-Path $localRemoteArchive) { Remove-Item $localRemoteArchive -Force }

    scp "$($sshTarget):$remoteArchivePath" "$localRemoteArchive"

    $cleanupCmd = "rm -f $remoteArchivePath"
    ssh $sshTarget $cleanupCmd
}
