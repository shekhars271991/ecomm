import aerospike

# -------------------------------
# CONFIGURE CONNECTION
# -------------------------------
config = {
    'hosts': [('127.0.0.1', 3000)]
}

try:
    client = aerospike.client(config).connect()
    print("Connected to Aerospike!")

    # -------------------------------
    # INSERT a record
    # -------------------------------
    key = ('test', 'demo', 'mykey')  # (namespace, set, key)
    bins = {
        'name': 'Alice',
        'age': 30
    }
    client.put(key, bins)
    print("Record written:", bins)

    # -------------------------------
    # GET the record
    # -------------------------------
    (key, metadata, record) = client.get(key)
    print("Record read:", record)

    # -------------------------------
    # UPDATE the record
    # -------------------------------
    updated_bins = {
        'age': 31
    }
    client.put(key, updated_bins)
    print("Record updated.")

    # GET updated record
    (_, _, updated_record) = client.get(key)
    print("Updated record:", updated_record)

    # -------------------------------
    # DELETE the record
    # -------------------------------
    client.remove(key)
    print("Record deleted.")

except Exception as e:
    print("Error:", e)

finally:
    client.close()
    print("Connection closed.")
