set -e

mongosh <<EOF

db = db.getSiblingDB('$DB_DATABASE');
db.createUser({
  user: '$DB_USERNAME',
  pwd: '$DB_PASSWORD',
  roles: [{ role: 'readWrite', db: '$DB_DATABASE' }]
});

db.reactions.createIndex(
   {
      "target_id": 1,
      "object_id": 1,
      "type": 1
   },
   { unique: true }
);
EOF
