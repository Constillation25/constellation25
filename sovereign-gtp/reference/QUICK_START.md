# SovereignGTP Quick Reference

## Start the Mesh
cd ~/constellation25/sovereign-gtp
./boot_mesh.sh

## Send Tasks
# Single task
./send_task.sh helio A_landing_page "Build hero section with biometric focus"
# Batch of 100 tasks
./batch_send.sh vault B_compliance 25 0.1

## Monitor
./monitor_tasks.sh
tail -f logs/helio.log
tail -f logs/totalrecall.log

## Check Outputs
ls -lh outputs/
cat outputs/helio_*_A_landing_page*.txt
python3 totalrecall/logger.py --verify

## Stop the Mesh
./stop_mesh.sh

## Agent Categories
| Agent | Specialization | Task Categories |
|-------|---------------|----------------|
| helio | Landing Pages | A_landing_page, F_videocourts_ui |
| vault | Compliance | B_compliance, H_totalrecall |
| echo | Investor Materials | C_investor, J_sovereigndeck |
| chronos | County Pilot | D_county_pilot |
| mercury | Marketing | E_marketing |
| venus | UI/UX Design | F_videocourts_ui, C_investor |
| earth | Legal AI | G_legal_ai, I_pathos_nlp |
| mars | Security/Forensics | B_compliance, H_totalrecall |

## Task Format
{
  "task_id": "unique_id",
  "agent": "agent_name",
  "type": "category_name",
  "payload": "natural language instruction",
  "timestamp": "ISO8601",
  "sender": "cli|batch|api",
  "priority": "normal|high|critical"
}

## Troubleshooting
- Agent not starting? Check logs/<agent>.log
- Tasks not processing? Verify tasks/incoming/ has JSON files
- No outputs? Check agent has write permissions to outputs/
- Chain broken? Run python3 totalrecall/logger.py --verify
