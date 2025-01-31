#!/usr/bin/env python3

import argparse
import logging
import logging.handlers
import requests
import sys

class CloudflareDNSUpdater:
    def __init__(self, api_token, domain, force=False):
        self.api_token = api_token
        self.domain = domain
        self.force = force
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to output to both STDOUT and syslog."""
        self.logger = logging.getLogger("CloudflareDNSUpdater")
        self.logger.setLevel(logging.INFO)

        # Log to STDOUT
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(stdout_handler)

        # Log to syslog
        syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
        syslog_handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(syslog_handler)

    def get_public_ip(self):
        """Retrieve the public IP address of the server."""
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()
            return response.json()["ip"]
        except Exception as e:
            self.logger.error(f"Failed to retrieve public IP: {e}")
            sys.exit(1)

    def get_zone_id(self):
        """Retrieve the zone ID for the domain."""
        try:
            response = requests.get(f"{self.base_url}/zones", headers=self.headers, params={"name": self.domain})
            response.raise_for_status()
            zones = response.json()["result"]
            if not zones:
                self.logger.error(f"No zone found for domain: {self.domain}")
                sys.exit(1)
            return zones[0]["id"]
        except Exception as e:
            self.logger.error(f"Failed to retrieve zone ID: {e}")
            sys.exit(1)

    def get_record_id(self, zone_id):
        """Retrieve the DNS record ID for the domain."""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=self.headers,
                params={"name": self.domain, "type": "A"},
            )
            response.raise_for_status()
            records = response.json()["result"]
            if not records:
                self.logger.error(f"No A record found for domain: {self.domain}")
                sys.exit(1)
            return records[0]["id"]
        except Exception as e:
            self.logger.error(f"Failed to retrieve DNS record ID: {e}")
            sys.exit(1)

    def get_current_record_ip(self, zone_id, record_id):
        """Retrieve the current IP address in the DNS record."""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()["result"]["content"]
        except Exception as e:
            self.logger.error(f"Failed to retrieve current DNS record IP: {e}")
            sys.exit(1)

    def update_dns_record(self, zone_id, record_id, new_ip):
        """Update the DNS record with the new IP address."""
        try:
            data = {"type": "A", "name": self.domain, "content": new_ip}
            response = requests.put(
                f"{self.base_url}/zones/{zone_id}/dns_records/{record_id}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            self.logger.info(f"Successfully updated DNS record for {self.domain} to {new_ip}")
        except Exception as e:
            self.logger.error(f"Failed to update DNS record: {e}")
            sys.exit(1)

    def run(self):
        """Execute the DNS update process."""
        self.logger.info("Starting DNS update process...")

        # Retrieve the server's public IP
        public_ip = self.get_public_ip()
        self.logger.info(f"Server's public IP address: {public_ip}")

        # Retrieve zone ID and record ID
        zone_id = self.get_zone_id()
        record_id = self.get_record_id(zone_id)

        # Retrieve current DNS record IP
        current_ip = self.get_current_record_ip(zone_id, record_id)
        self.logger.info(f"Current DNS record IP address: {current_ip}")

        # Compare IPs and update if necessary
        if current_ip != public_ip or self.force:
            self.logger.info("IP addresses differ or --force flag is set. Updating DNS record...")
            self.update_dns_record(zone_id, record_id, public_ip)
        else:
            self.logger.info("DNS record is already up to date. No changes made.")

        self.logger.info("DNS update process completed.")


def main():
    parser = argparse.ArgumentParser(description="Update Cloudflare DNS A record with the server's public IP.")
    parser.add_argument("api_token", help="Cloudflare API token")
    parser.add_argument("domain", help="Domain name to update")
    parser.add_argument("--force", action="store_true", help="Force update even if IP is unchanged")
    args = parser.parse_args()

    updater = CloudflareDNSUpdater(args.api_token, args.domain, args.force)
    updater.run()


if __name__ == "__main__":
    main()
