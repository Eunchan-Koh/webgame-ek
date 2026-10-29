---
name: windows-notify
description: 사용자가 검증하거나 답변해야 하는 내용이 있을 때만 Windows 알림(토스트)을 띄운다. 작업 중간에 사용자의 확인·답변을 기다려야 할 때(AskUserQuestion으로 질문하기 직전 등) 사용한다.
---

# windows-notify

사용자가 검증하거나 답변해야 하는 내용이 있을 때만 Windows 알림을 띄운다.

## 언제 쓰나

- 사용자가 결과를 검증해야 할 때
- 사용자의 답변이 필요할 때 (AskUserQuestion으로 질문할 때는 질문 직전에 띄운다)

그 외(진행 상황 보고, 사용자 확인이 필요 없는 작업 완료 등)에는 띄우지 않는다.

## Stop 훅과의 관계

- `.claude/settings.json`의 Stop 훅이 응답이 끝날 때마다 `hook.ps1`로 알림을 띄운다. 내용은 Claude의 마지막 응답이다.
- 응답을 끝내면서 검증·답변을 요청하는 경우는 Stop 훅 알림으로 충분하므로 이 스킬을 따로 쓰지 않는다 (알림이 두 번 뜨지 않게).
- 이 스킬은 응답이 끝나지 않은 채 사용자를 기다리는 경우(AskUserQuestion 등)에 쓴다.

## 쓰는 법

PowerShell에서 실행한다. 한글 문구를 명령줄 인자로 넘기면 깨질 수 있으므로 PowerShell 도구에서 직접 실행한다 (Bash에서 넘기지 않는다).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<프로젝트 루트>\.claude\skills\windows-notify\notify.ps1" -Title "<제목>" -Message "<내용>"
```

- 제목: `[검증 필요] <작업 이름>` 또는 `[답변 필요] <작업 이름>`
- 내용: 무엇을 확인·결정해야 하는지 한두 문장. 짧게 쓴다.

## 파일

- `notify.ps1`: 토스트를 띄운다.
- `hook.ps1`: Stop 훅이 호출한다.

## 주의

- 두 `.ps1` 파일은 Windows PowerShell 5.1이 한글을 읽도록 UTF-8(BOM 포함)으로 저장되어 있다. 고칠 때 인코딩을 유지한다.
- 알림이 실패해도 작업은 계속한다. 실패하면 그 사실을 보고에 적는다.
