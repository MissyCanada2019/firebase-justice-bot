import Cloudflare from 'cloudflare';

const cf = new Cloudflare({
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
});

export async function listDnsRecords(zoneId: string) {
  if (!zoneId) {
    throw new Error('A Cloudflare Zone ID is required.');
  }

  try {
    const records = await cf.dns.records.list({ zone_id: zoneId });
    return records;
  } catch (error) {
    console.error('Error listing DNS records:', error);
    throw error;
  }
}