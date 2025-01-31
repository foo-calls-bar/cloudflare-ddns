### Example Usage:
1. **Normal Update**:
   ```bash
   python3 cloudflare-ddns-updater.py your_api_token your_email@example.com yourdomain.com
   ```

2. **Force Update**:
   ```bash
   python3 cloudflare-ddns-updater.py your_api_token your_email@example.com yourdomain.com --force
   ```

### Example Logs in Syslog:
- **Normal Update**:
  ```
  cloudflare_dns_updater: INFO Public IP address: 192.0.2.1
  cloudflare_dns_updater: INFO Current DNS record IP: 192.0.2.1
  cloudflare_dns_updater: INFO DNS record is already up to date. No update needed.
  ```

- **Force Update**:
  ```
  cloudflare_dns_updater: INFO Public IP address: 192.0.2.1
  cloudflare_dns_updater: INFO Current DNS record IP: 192.0.2.1
  cloudflare_dns_updater: INFO Force update requested. Updating DNS record...
  cloudflare_dns_updater: INFO DNS record updated successfully: {...}
  ```

- **Outdated DNS Record**:
  ```
  cloudflare_dns_updater: INFO Public IP address: 192.0.2.2
  cloudflare_dns_updater: INFO Current DNS record IP: 192.0.2.1
  cloudflare_dns_updater: INFO DNS record is outdated. Updating...
  cloudflare_dns_updater: INFO DNS record updated successfully: {...}
  ```

### Example Logs In the Terminal (STDOUT)
- **Normal Update**:
```
2023-10-25 12:34:56,789 - cloudflare_dns_updater - INFO - Public IP address: 192.0.2.1
2023-10-25 12:34:57,123 - cloudflare_dns_updater - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - cloudflare_dns_updater - INFO - DNS record is already up to date. No update needed.
```

- **Forced Update**:
```
2023-10-25 12:34:56,789 - cloudflare_dns_updater - INFO - Public IP address: 192.0.2.1
2023-10-25 12:34:57,123 - cloudflare_dns_updater - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - cloudflare_dns_updater - INFO - Force update requested. Updating DNS record...
2023-10-25 12:34:57,456 - cloudflare_dns_updater - INFO - DNS record updated successfully: {...}
```

- **Outdated DNS Record**:
```
2023-10-25 12:34:56,789 - cloudflare_dns_updater - INFO - Public IP address: 192.0.2.2
2023-10-25 12:34:57,123 - cloudflare_dns_updater - INFO - Current DNS record IP: 192.0.2.1
2023-10-25 12:34:57,456 - cloudflare_dns_updater - INFO - DNS record is outdated. Updating...```
2023-10-25 12:34:57,456 - cloudflare_dns_updater - INFO - DNS record updated successfully: {...}
```

- Run as a cron job every five minutes or so to keep your cloudflare A records synced with the dynamic IP address of your server. By default won't do anything if current record matches IP. Use '--force' to force update.
