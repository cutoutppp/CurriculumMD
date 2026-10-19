import urllib.request
import urllib.parse
import json
import sys

# Ensure UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyCGjC6w1a795yZ858-V3q9-wD2_8zH1770"
PROJECT_ID = "tradesimschool"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/survey_config"

def get_doc(doc_id):
    encoded_id = urllib.parse.quote(doc_id)
    url = f"{BASE_URL}/{encoded_id}?key={API_KEY}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def set_doc(doc_id, fields):
    encoded_id = urllib.parse.quote(doc_id)
    url = f"{BASE_URL}/{encoded_id}?key={API_KEY}"
    data = json.dumps({"fields": fields}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='PATCH')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def delete_doc(doc_id):
    encoded_id = urllib.parse.quote(doc_id)
    url = f"{BASE_URL}/{encoded_id}?key={API_KEY}"
    req = urllib.request.Request(url, method='DELETE')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def main():
    old_id = "sgs_2569_2_ค2010"
    new_id = "sgs_2569_2_ค20210"

    print(f"=== Migrating Firestore Document: {old_id} -> {new_id} ===")
    
    # 1. Fetch old document
    old_doc = get_doc(old_id)
    if not old_doc:
        print(f"Old document {old_id} not found!")
        return

    print(f"Found {old_id}:")
    print(json.dumps(old_doc, ensure_ascii=False, indent=2))

    # 2. Prepare fields for new document
    fields = old_doc.get("fields", {})
    if "course_code" in fields:
        fields["course_code"] = {"stringValue": "ค20210"}

    # 3. Write new document
    print(f"\nWriting new document {new_id}...")
    created = set_doc(new_id, fields)
    print(f"Successfully wrote {new_id}:")
    print(json.dumps(created, ensure_ascii=False, indent=2))

    # 4. Verify new document exists
    verify = get_doc(new_id)
    if verify:
        print(f"\n[VERIFIED] {new_id} exists in Firestore!")
        print(f"Course code in new doc: {verify['fields']['course_code']['stringValue']}")
    else:
        print(f"\n[ERROR] Failed to verify {new_id}!")
        return

    # 5. Delete old document
    print(f"\nDeleting old document {old_id}...")
    deleted = delete_doc(old_id)
    print(f"Delete response: {deleted}")

    # 6. Verify old document is gone
    check_old = get_doc(old_id)
    if check_old is None:
        print(f"[VERIFIED] {old_id} successfully deleted from Firestore (HTTP 404).")
    else:
        print(f"[WARNING] {old_id} still exists!")

if __name__ == '__main__':
    main()
