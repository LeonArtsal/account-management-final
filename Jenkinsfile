#!/usr/bin/env groovy

dockerBuildTagPush {
    // "latest" is here, but argo is told about git-checksum tags, so it isn't used.
    imageTag = "account-management:latest"

    // which argo repo to update version pinning
    argoRepo = 'ssh://git@bitbucket.absolute.com:7999/argo/deploy-dp-account-management-tool.git'
    // update argo version pinning using git tags
    argoUseGitTag = true

    slackOnlyOnErr = true
}
