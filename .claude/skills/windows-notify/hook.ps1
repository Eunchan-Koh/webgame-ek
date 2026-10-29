param(
    [Parameter(Mandatory = $true)][ValidateSet('stop')][string]$Kind
)

# Claude Code Stop 훅에서 호출한다. 훅 입력(JSON, stdin)에서 Claude의 마지막 응답을 꺼내 알림 내용으로 쓴다.
# 한글이 깨지지 않도록 stdin은 UTF-8로 읽고, 고정 문구는 이 파일(UTF-8 BOM) 안에 둔다.
$title = '[작업 완료] Claude'
$message = ''

try {
    $reader = New-Object System.IO.StreamReader([Console]::OpenStandardInput(), [System.Text.Encoding]::UTF8)
    $payload = $reader.ReadToEnd() | ConvertFrom-Json

    if ($payload.last_assistant_message) {
        $message = [string]$payload.last_assistant_message
    }
    elseif ($payload.transcript_path -and (Test-Path -LiteralPath $payload.transcript_path)) {
        # 트랜스크립트(JSONL)에서 텍스트가 있는 마지막 assistant 메시지를 찾는다.
        $lines = Get-Content -LiteralPath $payload.transcript_path -Encoding UTF8
        for ($i = $lines.Count - 1; $i -ge 0 -and -not $message; $i--) {
            try { $entry = $lines[$i] | ConvertFrom-Json } catch { continue }
            if ($entry.type -ne 'assistant') { continue }
            $texts = @($entry.message.content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text })
            if ($texts.Count -gt 0) { $message = $texts -join "`n" }
        }
    }
}
catch { }

# 마크다운 기호를 걷어내고 알림 창에 맞게 줄인다.
$message = $message -replace '\[([^\]]*)\]\([^)]*\)', '$1' -replace '[`*#|>]', '' -replace '\s+', ' '
$message = $message.Trim()
if ($message.Length -gt 250) { $message = $message.Substring(0, 250) + '…' }
if (-not $message) { $message = '응답이 끝났습니다.' }

& "$PSScriptRoot\notify.ps1" -Title $title -Message $message
