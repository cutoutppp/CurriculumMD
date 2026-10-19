import urllib.request
import urllib.parse
import json
import sys

def check_firestore():
    api_key = "AIzaSyCGjC6w1a795yZ858-V3q9-wD2_8zH1770"
    project_id = "tradesimschool"

    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/survey_config?pageSize=300&key={api_key}"
    print(f"Connecting to Firestore for project {project_id}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            docs = data.get('documents', [])
            print(f"Total documents returned in survey_config: {len(docs)}")
            
            sgs_docs = []
            for d in docs:
                raw_name = d['name'].split('/')[-1]
                decoded_name = urllib.parse.unquote(raw_name)
                if 'sgs_2569_2_' in decoded_name:
                    sgs_docs.append((decoded_name, raw_name, d))

            print(f"Total sgs_2569_2_* documents: {len(sgs_docs)}")
            
            target_codes = ['ค2010', 'งง30226', 'ค20210', 'ง30226']
            print("\n--- Checking Target Courses in Firestore ---")
            for code in target_codes:
                doc_name = f"sgs_2569_2_{code}"
                matches = [item for item in sgs_docs if item[0] == doc_name]
                if matches:
                    print(f"[FOUND] {doc_name} exists in Firestore!")
                    print(f"  Document details: {json.dumps(matches[0][2], ensure_ascii=False, indent=2)}")
                else:
                    print(f"[NOT FOUND] {doc_name} does NOT exist in Firestore.")

            print("\n--- All Confirmed sgs_2569_2_* Documents ---")
            for doc_name, _, _ in sorted(sgs_docs, key=lambda x: x[0]):
                print(f"  - {doc_name}")

            # Check next page token if any
            if 'nextPageToken' in data:
                print(f"\nWarning: nextPageToken exists: {data['nextPageToken']}")

    except Exception as e:
        print(f"Error checking Firestore: {e}", file=sys.stderr)

if __name__ == '__main__':
    check_firestore()
