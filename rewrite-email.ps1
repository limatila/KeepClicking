param(
    [string]$Remote = "origin",
    [string]$NewBranch = "email-corrected-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & git @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')"
    }
}

# Confirm that the current directory is a Git repository.
& git rev-parse --is-inside-work-tree *> $null

if ($LASTEXITCODE -ne 0) {
    throw "The current directory is not inside a Git repository."
}

# Require a clean working tree.
$Status = & git status --porcelain

if ($LASTEXITCODE -ne 0) {
    throw "Could not inspect the Git working tree."
}

if ($Status) {
    throw "The working tree is not clean. Commit or stash your changes first."
}

# Read the identity specifically from the repository-local configuration.
$LocalName = (& git config --local --get user.name).Trim()
$LocalEmail = (& git config --local --get user.email).Trim()

if (-not $LocalName) {
    throw "No local user.name configured. Run: git config --local user.name `"Your Name`""
}

if (-not $LocalEmail) {
    throw "No local user.email configured. Run: git config --local user.email `"you@example.com`""
}

# Validate the remote.
& git remote get-url $Remote *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Remote '$Remote' does not exist."
}

# Validate the new branch name.
& git check-ref-format --branch $NewBranch *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Invalid branch name: $NewBranch"
}

# Prevent accidental reuse of an existing branch.
& git show-ref --verify --quiet "refs/heads/$NewBranch"

if ($LASTEXITCODE -eq 0) {
    throw "The local branch '$NewBranch' already exists."
}

$SourceBranch = (& git branch --show-current).Trim()

if (-not $SourceBranch) {
    $SourceBranch = "detached HEAD"
}

Write-Host "Source branch : $SourceBranch"
Write-Host "New branch    : $NewBranch"
Write-Host "New identity  : $LocalName <$LocalEmail>"
Write-Host "Remote        : $Remote"
Write-Host ""

# Create a separate branch so the original branch is preserved.
Invoke-Git -Arguments @("switch", "-c", $NewBranch)

# Variables consumed by Git's shell-based env-filter.
$env:FILTER_BRANCH_SQUELCH_WARNING = "1"
$env:CORRECTED_GIT_NAME = $LocalName
$env:CORRECTED_GIT_EMAIL = $LocalEmail

$EnvFilter = @'
export GIT_AUTHOR_NAME="$CORRECTED_GIT_NAME"
export GIT_AUTHOR_EMAIL="$CORRECTED_GIT_EMAIL"
export GIT_COMMITTER_NAME="$CORRECTED_GIT_NAME"
export GIT_COMMITTER_EMAIL="$CORRECTED_GIT_EMAIL"
'@

try {
    Invoke-Git -Arguments @(
        "filter-branch",
        "--force",
        "--env-filter",
        $EnvFilter,
        "--",
        $NewBranch
    )
}
finally {
    Remove-Item Env:\CORRECTED_GIT_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:\CORRECTED_GIT_EMAIL -ErrorAction SilentlyContinue
    Remove-Item Env:\FILTER_BRANCH_SQUELCH_WARNING -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Rewritten commits:"
Invoke-Git -Arguments @(
    "log",
    "--format=%h  %an <%ae>  %s",
    "--max-count=20"
)

Write-Host ""
Write-Host "Attempting to push the new branch..."

try {
    Invoke-Git -Arguments @(
        "push",
        "--set-upstream",
        $Remote,
        $NewBranch
    )

    Write-Host ""
    Write-Host "Successfully pushed: $Remote/$NewBranch"
}
catch {
    Write-Warning "The commits were rewritten locally, but the push failed."
    Write-Host "Retry with:"
    Write-Host "git push --set-upstream $Remote $NewBranch"
    throw
}