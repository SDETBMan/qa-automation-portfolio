# ─────────────────────────────────────────────────────────────────────────────
# QA Automation Portfolio — root Makefile
#
# Usage:
#   make              → print available targets
#   make all          → run all five frameworks sequentially
#   make playwright   → playwright-dotnet (C# + TypeScript, headless Chromium)
#   make selenium     → selenium-java (headless Chrome)
#   make cucumber     → cucumber (headless Chrome)
#   make ai-eval      → ai-eval (Python + Pytest + DeepEval)
#   make postman      → postman (Newman CLI, JSONPlaceholder API tests)
#   make clean        → remove build artefacts from all frameworks
#
# Prerequisites:
#   playwright — .NET 8 SDK (dotnet --version) · Node.js 20+ (node --version)
#   selenium   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   cucumber   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   ai-eval    — Python 3.11+ (python3 --version) · OPENAI_API_KEY in ai-eval/.env
#   postman    — Node.js 20+ (node --version)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help all playwright selenium cucumber cucumber-python ai-eval postman job-agent coding-agent fastapi-service fastapi-service-test cypress-test cypress-open k8s-apply k8s-delete k8s-status terraform-init terraform-validate terraform-fmt terraform-plan terraform-apply terraform-destroy terraform-clean clean

# Print help when `make` is called with no target
help:
	@echo ""
	@echo "  QA Automation Portfolio — available targets"
	@echo "  ───────────────────────────────────────────"
	@echo "  make all                  Run all five frameworks sequentially
  make cucumber-python      Run cucumber-python suite (Behave, headless Chrome)"
	@echo "  make cypress-test         Run Cypress E2E suite (headless Chrome)"
	@echo "  make cypress-open         Open Cypress interactive Test Runner"
	@echo "  make coding-agent         Run coding-agent demo suite (requires ANTHROPIC_API_KEY)"
	@echo "  make job-agent            Run Claude-powered job search agent"
	@echo "  make playwright           Run playwright-dotnet suite (C# + TypeScript)"
	@echo "  make selenium             Run selenium-java suite (headless Chrome)"
	@echo "  make cucumber             Run cucumber suite (headless Chrome)"
	@echo "  make ai-eval              Run AI evaluation suite (Python + DeepEval)"
	@echo "  make postman              Run Postman/Newman API test suite"
	@echo "  make fastapi-service      Start FastAPI server on :8001"
	@echo "  make fastapi-service-test Run FastAPI pytest suite"
	@echo "  make k8s-apply            Deploy Selenium Grid + Healenium to Kubernetes"
	@echo "  make k8s-delete           Tear down the selenium-grid namespace"
	@echo "  make k8s-status           Show pod status in the selenium-grid namespace"
	@echo "  make terraform-init       terraform init"
	@echo "  make terraform-validate   terraform validate"
	@echo "  make terraform-fmt        terraform fmt -recursive"
	@echo "  make terraform-plan       terraform plan"
	@echo "  make terraform-apply      terraform apply"
	@echo "  make terraform-destroy    terraform destroy"
	@echo "  make terraform-clean      Remove .terraform/ and state files"
	@echo "  make clean                Remove build artefacts from all frameworks"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    playwright       — .NET 8 SDK · Node.js 20+"
	@echo "    selenium         — Java 17 · Maven 3.9+"
	@echo "    cucumber         — Java 17 · Maven 3.9+"
	@echo "    cucumber-python  — Python 3.11+ · Chrome/Chromium installed"
	@echo "    ai-eval          — Python 3.11+ · OPENAI_API_KEY in ai-eval/.env"
	@echo "    postman          — Node.js 20+"
	@echo "    coding-agent     — Python 3.11+ · ANTHROPIC_API_KEY in coding-agent/.env"
	@echo "    job-agent        — Python 3.11+ · ANTHROPIC_API_KEY · TAVILY_API_KEY in job-agent/.env"
	@echo "    fastapi-service  — Python 3.11+"
	@echo "    cypress          — Node.js 20+"
	@echo "    k8s              — kubectl · running cluster or Kind (kind.sigs.k8s.io)"
	@echo "    terraform        — Terraform >= 1.6 · AWS credentials · DataDog API/App keys"
	@echo ""

# ── Full portfolio ─────────────────────────────────────────────────────────────

all: playwright selenium cucumber ai-eval postman
	@echo ""
	@echo ">>> All five suites complete."
	@echo ""

# ── Individual suites ─────────────────────────────────────────────────────────

playwright:
	@echo ""
	@echo ">>> [playwright-dotnet] Running C# + TypeScript suite..."
	$(MAKE) -C playwright-dotnet all
	@echo ""
	@echo ">>> [playwright-dotnet] Done."
	@echo ""

selenium:
	@echo ""
	@echo ">>> [selenium-java] Running headless Chrome suite..."
	cd selenium-java && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [selenium-java] Done."
	@echo ""

cucumber:
	@echo ""
	@echo ">>> [cucumber] Running headless Chrome suite..."
	cd cucumber && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [cucumber] Done."
	@echo ""

cucumber-python:
	@echo ""
	@echo ">>> [cucumber-python] Installing dependencies and running Behave suite..."
	cd cucumber_python && pip install -r requirements.txt -q && \
		HEADLESS=true behave --no-capture
	@echo ""
	@echo ">>> [cucumber-python] Done."
	@echo ""

ai-eval:
	@echo ""
	@echo ">>> [ai-eval] Installing dependencies and running DeepEval suite..."
	cd ai-eval && pip install -r requirements.txt -q && pytest -v
	@echo ""
	@echo ">>> [ai-eval] Done."
	@echo ""

postman:
	@echo ""
	@echo ">>> [postman] Installing Newman and running API test suite..."
	cd postman && npm install && npm test
	@echo ""
	@echo ">>> [postman] Done."
	@echo ""

coding-agent:
	@echo ""
	@echo ">>> [coding-agent] Installing dependencies and running Demo 2 (feedback loop)..."
	cd coding-agent && pip install -r requirements.txt -q && python run_demo.py --demo 2
	@echo ""
	@echo ">>> [coding-agent] Done. Output in coding-agent/output/"
	@echo ""

job-agent:
	@echo ""
	@echo ">>> [job-agent] Running job search..."
	cd job-agent && pip install -r requirements.txt -q && python run.py
	@echo ""
	@echo ">>> [job-agent] Done. Results in job-agent/output/"
	@echo ""

fastapi-service:
	@echo ""
	@echo ">>> [fastapi-service] Starting API server..."
	cd fastapi-service && pip install -r requirements.txt -q && \
		uvicorn app.main:app --reload --port 8001
	@echo ""

fastapi-service-test:
	@echo ""
	@echo ">>> [fastapi-service] Running tests..."
	cd fastapi-service && pip install -r requirements.txt -q && \
		pytest tests/ -v --cov=app --cov-report=term-missing
	@echo ""

cypress-test:
	@echo ""
	@echo ">>> [cypress] Running Cypress tests..."
	cd cypress && npm ci --quiet && npm test
	@echo ""

cypress-open:
	@echo ""
	@echo ">>> [cypress] Opening Cypress Test Runner..."
	cd cypress && npm ci --quiet && npx cypress open
	@echo ""

# ── Kubernetes ────────────────────────────────────────────────────────────────

k8s-apply:
	@echo ""
	@echo ">>> [k8s] Applying manifests to cluster..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/selenium-grid/
	kubectl apply -f k8s/healenium/
	@echo ""
	@echo ">>> [k8s] Manifests applied. Run 'make k8s-status' to check readiness."
	@echo ""

k8s-delete:
	@echo ""
	@echo ">>> [k8s] Deleting selenium-grid namespace..."
	kubectl delete namespace selenium-grid --ignore-not-found
	@echo ""
	@echo ">>> [k8s] Namespace deleted."
	@echo ""

k8s-status:
	@echo ""
	@echo ">>> [k8s] Pod status in selenium-grid namespace:"
	@echo ""
	kubectl get pods -n selenium-grid
	@echo ""

## ── Terraform ────────────────────────────────────────────────────────────────

terraform-init:
	cd terraform && terraform init

terraform-validate: terraform-init
	cd terraform && terraform validate

terraform-fmt:
	cd terraform && terraform fmt -recursive

terraform-plan: terraform-init
	cd terraform && terraform plan

terraform-apply: terraform-init
	cd terraform && terraform apply

terraform-destroy: terraform-init
	cd terraform && terraform destroy

terraform-clean:
	rm -rf terraform/.terraform terraform/.terraform.lock.hcl terraform/terraform.tfstate*

# ── Clean ─────────────────────────────────────────────────────────────────────

clean:
	@echo ""
	@echo ">>> Cleaning playwright-dotnet artefacts..."
	$(MAKE) -C playwright-dotnet clean
	@echo ""
	@echo ">>> Cleaning selenium-java artefacts..."
	cd selenium-java && mvn clean
	@echo ""
	@echo ">>> Cleaning cucumber artefacts..."
	cd cucumber && mvn clean
	@echo ""
	@echo ">>> Cleaning cucumber-python artefacts..."
	rm -rf cucumber_python/reports cucumber_python/__pycache__ cucumber_python/**/__pycache__
	@echo ""
	@echo ">>> Cleaning coding-agent artefacts..."
	rm -rf coding-agent/output/* coding-agent/__pycache__ coding-agent/**/__pycache__
	touch coding-agent/output/.gitkeep
	@echo ""
	@echo ">>> Cleaning ai-eval artefacts..."
	rm -rf ai-eval/.pytest_cache ai-eval/.deepeval ai-eval/__pycache__
	@echo ""
	@echo ">>> Cleaning postman artefacts..."
	rm -rf postman/node_modules postman/results/*.xml postman/results/*.html
	@echo ""
	@echo ">>> Clean complete."
	@echo ""
