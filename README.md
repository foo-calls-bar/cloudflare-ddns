### Usage:
   ```bash
   python3 cloudflare-ddns-updater.py <API_TOKEN> <DOMAIN> [--force]
   ```
### Example Logs in Syslog:
- **Normal Update**:
  ```
  CloudflareDNSUpdater: INFO Public IP address: 192.0.2.1
  CloudflareDNSUpdater: INFO Current DNS record IP: 192.0.2.1
  CloudflareDNSUpdater: INFO DNS record is already up to date. No update needed.
  ```

- **Force Update**:
  ```
  CloudflareDNSUpdater: INFO Public IP address: 192.0.2.1
  CloudflareDNSUpdater: INFO Current DNS record IP: 192.0.2.1
  CloudflareDNSUpdater: INFO Force update requested. Updating DNS record...
  CloudflareDNSUpdater: INFO DNS record updated successfully: {...}
  ```

- **Outdated DNS Record**:
  ```
  CloudflareDNSUpdater: INFO Public IP address: 192.0.2.2
  CloudflareDNSUpdater: INFO Current DNS record IP: 192.0.2.1
  CloudflareDNSUpdater: INFO DNS record is outdated. Updating...
  CloudflareDNSUpdater: INFO DNS record updated successfully: {...}
  ```

### Example Logs In the Terminal (STDOUT)
- **Normal Update**:
```
2023-10-25 12:34:56,789 - INFO - Public IP address: 192.0.2.1
2023-10-25 12:34:57,123 - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - INFO - DNS record is already up to date. No update needed.
```

- **Forced Update**:
```
2023-10-25 12:34:56,789 - INFO - Public IP address: 192.0.2.1
2023-10-25 12:34:57,123 - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - INFO - Force update requested. Updating DNS record...
2023-10-25 12:34:57,456 - INFO - DNS record updated successfully: {...}
```

- **Outdated DNS Record**:
```
2023-10-25 12:34:56,789 - INFO - Public IP address: 192.0.2.2
2023-10-25 12:34:57,123 - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - INFO - DNS record is outdated. Updating...```
2023-10-25 12:34:57,456 - INFO - DNS record updated successfully: {...}
```

- Run as a cron job every five minutes or so to keep your cloudflare A records synced with the dynamic IP address of your server. By default won't do anything if current record matches IP. Use '--force' to force update.
