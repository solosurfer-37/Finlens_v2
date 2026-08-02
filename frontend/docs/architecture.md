FinLens/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── investigations.py
│   │   │   ├── accounts.py
│   │   │   ├── graph.py
│   │   │   ├── reports.py
│   │   │   ├── history.py
│   │   │   ├── dashboard.py
│   │   │   ├── settings.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   │   │
│   │   ├── controllers/
│   │   │   ├── upload_controller.py
│   │   │   ├── investigation_controller.py
│   │   │   ├── graph_controller.py
│   │   │   ├── report_controller.py
│   │   │   ├── dashboard_controller.py
│   │   │   ├── account_controller.py
│   │   │   ├── history_controller.py
│   │   │   └── auth_controller.py
│   │   │
│   │   ├── services/
│   │   │   ├── csv_parser.py
│   │   │   ├── validator.py
│   │   │   ├── transaction_service.py
│   │   │   ├── account_service.py
│   │   │   ├── graph_builder.py
│   │   │   ├── investigation_service.py
│   │   │   ├── report_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── history_service.py
│   │   │   └── notification_service.py
│   │   │
│   │   ├── detectors/
│   │   │   ├── __init__.py
│   │   │   ├── large_transfer.py
│   │   │   ├── fan_out.py
│   │   │   ├── velocity.py
│   │   │   ├── cycle_detection.py
│   │   │   ├── dsu.py
│   │   │   ├── centrality.py
│   │   │   ├── benford.py
│   │   │   ├── structuring.py
│   │   │   ├── historical_baseline.py
│   │   │   └── watchlist.py
│   │   │
│   │   ├── engine/
│   │   │   ├── detection_engine.py
│   │   │   ├── scoring_engine.py
│   │   │   ├── evidence_engine.py
│   │   │   ├── recommendation_engine.py
│   │   │   └── alert_engine.py
│   │   │
│   │   ├── graph/
│   │   │   ├── graph.py
│   │   │   ├── node.py
│   │   │   ├── edge.py
│   │   │   ├── algorithms.py
│   │   │   ├── traversal.py
│   │   │   └── clustering.py
│   │   │
│   │   ├── ai/
│   │   │   ├── gemini_client.py
│   │   │   ├── prompts.py
│   │   │   ├── report_generator.py
│   │   │   ├── account_summary.py
│   │   │   └── recommendations.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── session.py
│   │   │   ├── seed.py
│   │   │   └── migrations/
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── investigation.py
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   ├── fraud_signal.py
│   │   │   ├── evidence.py
│   │   │   ├── report.py
│   │   │   └── notification.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── upload_schema.py
│   │   │   ├── account_schema.py
│   │   │   ├── transaction_schema.py
│   │   │   ├── investigation_schema.py
│   │   │   ├── report_schema.py
│   │   │   ├── dashboard_schema.py
│   │   │   └── auth_schema.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── account_repository.py
│   │   │   ├── transaction_repository.py
│   │   │   ├── investigation_repository.py
│   │   │   ├── report_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── notification_repository.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth.py
│   │   │   ├── logger.py
│   │   │   ├── error_handler.py
│   │   │   ├── rate_limiter.py
│   │   │   └── cors.py
│   │   │
│   │   ├── utils/
│   │   │   ├── constants.py
│   │   │   ├── helpers.py
│   │   │   ├── formatter.py
│   │   │   ├── logger.py
│   │   │   ├── enums.py
│   │   │   └── validators.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_upload.py
│   │   │   ├── test_graph.py
│   │   │   ├── test_detectors.py
│   │   │   ├── test_database.py
│   │   │   └── test_api.py
│   │   │
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── uploads/
│   │
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   │
│   ├── index.html
│   │
│   ├── pages/
│   │   ├── investigation.html
│   │   ├── processing.html
│   │   ├── dashboard.html
│   │   ├── graph.html
│   │   ├── account.html
│   │   ├── evidence.html
│   │   ├── timeline.html
│   │   ├── report.html
│   │   ├── history.html
│   │   ├── settings.html
│   │   └── about.html
│   │
│   ├── css/
│   │   ├── global.css
│   │   ├── variables.css
│   │   ├── typography.css
│   │   ├── layout.css
│   │   ├── animations.css
│   │   ├── navbar.css
│   │   ├── sidebar.css
│   │   ├── dashboard.css
│   │   ├── graph.css
│   │   ├── investigation.css
│   │   ├── account.css
│   │   ├── report.css
│   │   ├── tables.css
│   │   ├── forms.css
│   │   ├── components.css
│   │   └── responsive.css
│   │
│   ├── js/
│   │   ├── main.js
│   │   ├── api.js
│   │   ├── state.js
│   │   ├── router.js
│   │   ├── upload.js
│   │   ├── dashboard.js
│   │   ├── graph.js
│   │   ├── account.js
│   │   ├── report.js
│   │   ├── history.js
│   │   ├── settings.js
│   │   ├── notifications.js
│   │   └── utils.js
│   │
│   ├── components/
│   │   ├── navbar/
│   │   ├── sidebar/
│   │   ├── footer/
│   │   ├── summary-card/
│   │   ├── statistic-card/
│   │   ├── graph-panel/
│   │   ├── account-panel/
│   │   ├── evidence-panel/
│   │   ├── timeline/
│   │   ├── upload-form/
│   │   ├── search-bar/
│   │   ├── filters/
│   │   ├── modal/
│   │   ├── toast/
│   │   ├── loading/
│   │   ├── badge/
│   │   ├── button/
│   │   └── charts/
│   │
│   ├── services/
│   │   ├── uploadService.js
│   │   ├── graphService.js
│   │   ├── reportService.js
│   │   ├── accountService.js
│   │   ├── dashboardService.js
│   │   ├── historyService.js
│   │   └── notificationService.js
│   │
│   ├── assets/
│   │   ├── icons/
│   │   ├── logos/
│   │   ├── images/
│   │   ├── illustrations/
│   │   ├── fonts/
│   │   └── favicon/
│   │
│   ├── libs/
│   │   ├── vis-network/
│   │   ├── gsap/
│   │   ├── chartjs/
│   │   └── lenis/
│   │
│   └── README.md
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   ├── procedures.sql
│   ├── triggers.sql
│   ├── views.sql
│   ├── indexes.sql
│   ├── sample_data.sql
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── frontend.md
│   ├── backend.md
│   ├── database.md
│   ├── ui-flow.md
│   ├── workflow.md
│   ├── roadmap.md
│   ├── deployment.md
│   └── contribution.md
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│
├── .gitignore
├── LICENSE
├── README.md
└── CHANGELOG.md