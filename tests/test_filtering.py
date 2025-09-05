"""
Test the filtered field extraction on existing JSON files
"""
import json
import os

def test_field_filtering():
    """Test the field filtering on existing scraped files"""
    
    # Define the desired fields
    desired_fields = [
        "product_id", "name", "sku", "attribute_set_id", "attribute_set", 
        "type_id", "price", "min_price", "max_price", "min_price_format", 
        "max_price_format", "gold_weight", "none_metal_weight", "fixed_silver_weight", 
        "material_design", "qty", "collection", "collection_id", "product_type", 
        "product_type_value", "category", "category_name", "store_code", 
        "platinum_palladium_info_in_alloy", "bracelet_without_chain", 
        "show_popup_quantity_eternity", "visible_contents", "gender"
    ]
    
    output_dir = "data/scraped/output"
    filtered_dir = "data/scraped/output_filtered"
    
    # Create filtered output directory
    os.makedirs(filtered_dir, exist_ok=True)
    
    if not os.path.exists(output_dir):
        print("❌ No output directory found. Run the scraper first.")
        return
    
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ No JSON files found in output directory.")
        return
    
    print(f"🔍 Testing field filtering on {len(json_files)} existing files...")
    print()
    
    total_files = 0
    total_filtered_fields = 0
    
    for filename in json_files:
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter data to only include desired fields
            filtered_data = {}
            original_field_count = len(data)
            
            for field in desired_fields:
                if field in data:
                    filtered_data[field] = data[field]
            
            # Add metadata
            filtered_data['_metadata'] = {
                'original_file': filename,
                'extraction_timestamp': 'test_filtering',
                'fields_extracted': len(filtered_data) - 1,  # -1 for metadata
                'total_fields_available': original_field_count,
                'desired_fields_total': len(desired_fields)
            }
            
            # Save filtered version
            filtered_filepath = os.path.join(filtered_dir, f"filtered_{filename}")
            with open(filtered_filepath, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
            
            found_fields = len(filtered_data) - 1  # -1 for metadata
            total_filtered_fields += found_fields
            total_files += 1
            
            print(f"✅ {filename}")
            print(f"   Fields found: {found_fields}/{len(desired_fields)} ({found_fields/len(desired_fields)*100:.1f}%)")
            print(f"   Original size: {original_field_count} fields")
            print(f"   Filtered size: {found_fields} fields")
            
            # Show which fields were found
            found_field_names = [field for field in desired_fields if field in data]
            missing_field_names = [field for field in desired_fields if field not in data]
            
            if found_field_names:
                print(f"   ✅ Found: {', '.join(found_field_names[:5])}{'...' if len(found_field_names) > 5 else ''}")
            
            if missing_field_names:
                print(f"   ❌ Missing: {', '.join(missing_field_names[:3])}{'...' if len(missing_field_names) > 3 else ''}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    if total_files > 0:
        avg_fields = total_filtered_fields / total_files
        print("=" * 50)
        print("📊 FILTERING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {total_files}")
        print(f"Average fields found: {avg_fields:.1f}/{len(desired_fields)}")
        print(f"Success rate: {avg_fields/len(desired_fields)*100:.1f}%")
        print(f"Filtered files saved to: {filtered_dir}/")
        print()
        print("✅ Field filtering test completed!")
    else:
        print("❌ No files were processed successfully.")

if __name__ == "__main__":
    test_field_filtering()
