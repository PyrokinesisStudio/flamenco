from abstract_flamenco_test import AbstractFlamencoTest


class CreateManagerTest(AbstractFlamencoTest):
    def test_create_manager(self):
        from pillar.api.utils.authentication import force_cli_user
        from flamenco.setup import create_manager

        # Make sure the owner of the manager exists.
        owner_id = self.create_user(email='jemoeder@jevader.nl')

        with self.app.test_request_context():
            force_cli_user()
            mngr_doc, account, token = create_manager(
                'jemoeder@jevader.nl', 'Unit test mānāgèr', '¡Awesome in Space!')

        self.assertEqual('Unit test mānāgèr', mngr_doc['name'])

        self.assertEqual(f'SRV-{account["_id"]}', account['full_name'])
        self.assertEqual(f'SRV-{account["_id"]}', account['username'])
        self.assertEqual(['flamenco_manager', 'service'], account['roles'])
        self.assertEqual([], account['auth'])
        self.assertEqual({'flamenco_manager': {}}, account['service'])

        self.assertIn('owner', mngr_doc)
        self.assertTrue(mngr_doc['owner'])

        # Check that the group exists, and that it refers to the manager in its name.
        with self.app.test_request_context():
            groups_coll = self.app.db().groups
            group = groups_coll.find_one(mngr_doc['owner'])
            self.assertIn(str(mngr_doc['_id']), group['name'])

        self.assertAllowsAccess(token, account['_id'])

        # Check that the owner is now member of the owner group.
        owner = self.fetch_user_from_db(owner_id)
        self.assertIn(mngr_doc['owner'], owner['groups'])

    def test_manager_without_owner_email_address(self):
        from pillar.api.utils.authentication import force_cli_user
        from flamenco.setup import create_manager

        with self.app.test_request_context():
            force_cli_user()

            with self.assertRaises(ValueError):
                create_manager('', 'Unit test mānāgèr', '¡Awesome in Space!')

    def test_two_managers_with_same_owner(self):
        from pillar.api.utils.authentication import force_cli_user
        from flamenco.setup import create_manager

        self.create_user(email='jemoeder@jevader.nl')

        with self.app.test_request_context():
            force_cli_user()
            mngr_doc1, account1, token1 = create_manager('jemoeder@jevader.nl', 'mānāgèr 1', 'Awe!')
            mngr_doc2, account2, token2 = create_manager('jemoeder@jevader.nl', 'mānāgèr 2', 'som!')

        self.assertAllowsAccess(token1, account1['_id'])
        self.assertAllowsAccess(token2, account2['_id'])
