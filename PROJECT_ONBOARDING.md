{
  "protocol": "Phylosophy_AGI_Factory_Machine_Onboarding_v1",
  "bias_audit": {
    "status": "PASSED",
    "verified_biases": ["BIAS-016", "BIAS-034", "BIAS-035", "BIAS-036"],
    "auditor": "hallucination-and-bias-checker"
  },
  "financial_goals": {
    "goal_1_immediate": { "target_usdc": 100.0, "type": "NET_PROFIT_MILESTONE" },
    "goal_2_monthly": { "target_usd_month": 10000.0, "type": "AUTONOMOUS_PASSIVE" },
    "goal_3_target": { "target_usd_month": 500000.0, "type": "PASSIVE_OR_SEMI_PASSIVE" }
  },
  "infrastructure": {
    "tokyo_vps": {
      "ip": "54.168.247.83",
      "daemon": "x402.service",
      "endpoints": {
        "scrape_relay": "http://54.168.247.83:8402/api/v1/scrape",
        "health_check": "http://54.168.247.83:8402/api/v1/health",
        "analytics": "http://54.168.247.83:8402/api/v1/analytics",
        "dashboard": "http://54.168.247.83:8402/dashboard"
      }
    },
    "web3_settlement": {
      "primary_network": "base-mainnet",
      "dual_chain_extension": "polygon-pos",
      "wallet_address": "0x29C814FA1b67c23ec614bFc96C80f2274301cEBc",
      "strategy_2_funded_balance_usdc": 20.88
    },
    "alerting_system": {
      "telegram_bot": "@Psystarbot",
      "bot_token": "__REFER_TO_ENV__",
      "chat_id": "__REFER_TO_ENV__",
      "supervisor_daemon": "laptop_ollama_supervisor.py",
      "ping_interval_seconds": 10
    },
    "database": {
      "supabase_url": "https://omzmzksajenywuylksrx.supabase.co",
      "telemetry_table": "vps_telemetry_logs"
    }
  },
  "swarm_management": {
    "general_manager": "moonshotai/kimi-k3",
    "lead_execution_manager": "deepseek/deepseek-chat",
    "local_free_swarm": ["qwen3.5:4b", "hermes3:8b", "deepseek-r1"],
    "prioritization_formula": "Priority_Score = ((Organic_Demand * Expected_Net_USDC) / Dev_Hours) * Speed_Multiplier",
    "revenue_mantra": "Are we getting paid yet? If not, why? How to fix? Test again, are we getting paid now?"
  }
}
