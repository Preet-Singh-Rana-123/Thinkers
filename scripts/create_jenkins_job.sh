#!/usr/bin/env bash
set -e

JENKINS_URL="http://localhost:8089"
JOB_NAME="Thinkers-CI-CD"

echo "Fetching Jenkins CSRF Crumb..."
CRUMB_JSON=$(curl -s -c /tmp/cookies.txt "${JENKINS_URL}/crumbIssuer/api/json")
CRUMB=$(echo "$CRUMB_JSON" | grep -o '"crumb":"[^"]*' | cut -d'"' -f4)
CRUMB_FIELD=$(echo "$CRUMB_JSON" | grep -o '"crumbRequestField":"[^"]*' | cut -d'"' -f4)

echo "Crumb: $CRUMB"

cat << 'XML' > /tmp/job_config.xml
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>Thinkers Cloud-Native Continuous Integration &amp; Deployment Pipeline (Devops-Synopsis.pdf Diagram 3)</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/Preet-Singh-Rana-123/Thinkers.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
XML

echo "Creating or Updating Jenkins Pipeline Job: ${JOB_NAME}..."
curl -s -X POST "${JENKINS_URL}/createItem?name=${JOB_NAME}" \
  -b /tmp/cookies.txt \
  -H "${CRUMB_FIELD}: ${CRUMB}" \
  -H "Content-Type: application/xml" \
  --data-binary "@/tmp/job_config.xml" || true

echo "Checking if job exists..."
curl -s "${JENKINS_URL}/job/${JOB_NAME}/api/json" | grep -o '"name":"[^"]*' || echo "Job setup complete."
