from github import Github

#access token
g = Github("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")

def pushToGit():
    repo = g.get_repo("CoopGod/scheduling-site")