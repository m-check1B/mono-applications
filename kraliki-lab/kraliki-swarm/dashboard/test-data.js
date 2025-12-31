import { getFullStatus } from './src/lib/server/data.js';

async function test() {
    try {
        const status = await getFullStatus();
        console.log('Status keys:', Object.keys(status));
        console.log('Linear data:', status.linear ? 'Present' : 'Null');
        if (status.linear) {
            console.log('Linear issues count:', status.linear.issues.length);
            console.log('Linear stats:', status.linear.stats);
        }
    } catch (e) {
        console.error('Error:', e);
    }
}

test();
