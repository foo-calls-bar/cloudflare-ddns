#!/usr/bin/python3

import requests
import json
import sys
import logging
import logging.handlers

class CloudflareDNSUpdater:
    def __init__(self, api_token, email, domain, force_update=False):
        self.api_token = api_token
        self.email = email
        self.domain = domain
        self.force_update = force_update
        self.logger = self.setup_logging()

    def setup_logging(self):
        """Configure logging to use both SysLogHandler and StreamHandler."""
        logger = logging.getLogger('cloudflare_dns_updater')
        logger.setLevel(logging.INFO)

        # SysLogHandler for system logs
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')  # Use '/var/run/syslog' for macOS
        syslog_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
        syslog_handler.setFormatter(syslog_formatter)

        # StreamHandler for STDOUT
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stdout_handler.setFormatter(stdout_formatter)

        # Add both handlers
        logger.addHandler(syslog_handler)
        logger.addHandler(stdout_handler)

        return logger

    def get_public_ip(self):
        """Retrieve the public IP address of the server."""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()
            return response.json()['ip']
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error obtaining public IP: {e}")
            return None

    def get_zone_id(self):
        """Retrieve the zone ID for the domain."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-Auth-Email": self.email
        }
        try:
            response = requests.get(
                "https://api.cloudflare.com/client/v4/zones",
                headers=headers,
                params={"name": self.domain}
            )
            response.raise_for_status()
            zones = response.json()["result"]
            if zones:
                return zones[0]["id"]  # Return the first matching zone_id
            else:
                self.logger.error(f"No zone found for domain: {self.domain}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving zone ID: {e}")
            return None

    def get_dns_record_info(self, zone_id):
        """Retrieve the DNS record ID and current IP for the domain."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-Auth-Email": self.email
        }
        try:
            response = requests.get(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                headers=headers,
                params={"name": self.domain, "type": "A"}
            )
            response.raise_for_status()
            records = response.json()["result"]
            if records:
                return records[0]["id"], records[0]["content"]  # Return record ID and current IP
            else:
                self.logger.error(f"No DNS A record found for domain: {self.domain}")
                return None, None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error retrieving DNS record info: {e}")
            return None, None

    def update_dns_record(self, zone_id, record_id, ip_address):
        """Update the DNS A record with the new IP address."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "X-Auth-Email": self.email
        }
        data = {
            "type": "A",
            "name": self.domain,
            "content": ip_address,
            "ttl": 120,  # TTL in seconds
            "proxied": False  # Set to True if you want to proxy through Cloudflare
        }
        try:
            response = requests.put(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            self.logger.info(f"DNS record updated successfully: {response.json()}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating DNS record: {e}")

    def run(self):
        """Main method to execute the DNS update process."""
        public_ip = self.get_public_ip()
        if not public_ip:
            self.logger.error("Failed to obtain public IP address.")
            return

        self.logger.info(f"Public IP address: {public_ip}")

        zone_id = self.get_zone_id()
        if not zone_id:
            self.logger.error(f"Failed to retrieve zone ID for domain: {self.domain}")
            return

        record_id, current_ip = self.get_dns_record_info(zone_id)
        if not record_id:
            self.logger.error(f"Failed to retrieve DNS record ID for domain: {self.domain}")
            return

        self.logger.info(f"Current DNS record IP: {current_ip}")

        if current_ip == public_ip and not self.force_update:
            self.logger.info("DNS record is already up to date. No update needed.")
        else:
            if self.force_update:
                self.logger.info("Force update requested. Updating DNS record...")
            else:
                self.logger.info("DNS record is outdated. Updating...")
            self.update_dns_record(zone_id, record_id, public_ip)

if __name__ == "__main__":
    # Check if the required arguments are provided
    if len(sys.argv) < 4:
        print("Usage: python3 update_dns.py <api_token> <email> <domain> [--force]")
        sys.exit(1)

    # Parse command-line arguments
    api_token = sys.argv[1]
    email = sys.argv[2]
    domain = sys.argv[3]

    # Check for the --force flag
    force_update = "--force" in sys.argv

    # Create an instance of CloudflareDNSUpdater and run it
    updater = CloudflareDNSUpdater(api_token, email, domain, force_update)
    updater.run()
