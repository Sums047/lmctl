#!/usr/bin/env groovy

String tarquinBranch = "CPNA-1493"

library "tarquin@$tarquinBranch"

pipelinePy {
  pkgInfoPath = 'lmctl/pkg_info.json'
  applicationName = 'lmctl'
  attachDocsToRelease = true
  releaseToPypi = true
}
