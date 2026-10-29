param(
    [Parameter(Mandatory = $true)][string]$Title,
    [Parameter(Mandatory = $true)][string]$Message
)

# Windows 토스트 알림을 띄운다. Windows PowerShell 5.1의 WinRT API를 쓴다 (추가 모듈 없음).
$ErrorActionPreference = 'Stop'

[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$t = [System.Security.SecurityElement]::Escape($Title)
$m = [System.Security.SecurityElement]::Escape($Message)

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast scenario='reminder'><visual><binding template='ToastGeneric'><text>$t</text><text>$m</text></binding></visual><actions><action content='확인' arguments='dismiss' activationType='system'/></actions></toast>")

# 등록된 앱 ID가 있어야 알림이 뜬다. Windows PowerShell의 앱 ID를 쓴다.
$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
Write-Output "notified: $Title"
