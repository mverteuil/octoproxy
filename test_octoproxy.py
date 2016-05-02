import json

import octoproxy as proxy


class TestPullRequestEvents(object):
    def setup(self):
        self.event_data = {
            'pull_request': {
                'head': {'ref': 'feature-branch' },},
            'repository': {
                'name': 'testrepository',
                'full_name': 'testorg/testrepository',
            },
        }

    def test_proxy_closed_pull_request(self):
        with proxy.app.test_client() as client:
            self.event_data['action'] = 'closed'
            expected_data = json.dumps(self.event_data)
            response = client.post('/webhook/',
                                   headers={'X-GitHub-Event': 'pull_request',
                                            'Content-Type': 'application/json'},
                                   data=expected_data)
            assert response.status_code == 200
            assert response.data == expected_data
