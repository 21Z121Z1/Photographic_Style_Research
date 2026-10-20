// Explicit synthetic statistics, serialized by original CMI functions.
// The chosen numeric fields are a diagnostic fixture, never real camera stats.
static NSDictionary*S78StatsContext(void){
 typedef NSDictionary*(*DictionaryFn)(const void*);
 typedef void(*PopulateFn)(void*,NSDictionary*);
 NSMutableData*stats=[NSMutableData dataWithLength:0x2990];float*global=(float*)((char*)stats.mutableBytes+0x2800);
 const float fields[9]={.01f,.03f,.08f,.15f,.3f,.45f,.7f,.9f,1.f};
 for(int k=0;k<10;k++)memcpy(global+k*9,fields,sizeof(fields));
 float extra[2]={.25f,.5f};memcpy((char*)stats.mutableBytes+0x2970,extra,sizeof(extra));
 NSMutableArray*bindings=[NSMutableArray new];uint64_t addresses[]={0x2333d7b40ull,0x2333d7e14ull,0x2333d81a8ull,0x2333d81b4ull};
 for(int i=0;i<4;i++){NSDictionary*symbol=SymbolAt(addresses[i]+Slide75);Need([symbol[@"image"]containsString:@"/CMImaging.framework/"],@"original stats C entry image");[bindings addObject:@{@"unslid":Hex(addresses[i]),@"dladdr":symbol,@"first16_bytes_SHA256":SHA75(Read(addresses[i]+Slide75,16).bytes,16)}];}
 DictionaryFn dictionary=(DictionaryFn)(uintptr_t)(addresses[0]+Slide75),extended=(DictionaryFn)(uintptr_t)(addresses[1]+Slide75);
 PopulateFn populate=(PopulateFn)(uintptr_t)(addresses[2]+Slide75),populateExtended=(PopulateFn)(uintptr_t)(addresses[3]+Slide75);
 NSString*before=SHA75(stats.bytes,stats.length);NSDictionary*d=dictionary(stats.bytes),*x=extended(stats.bytes);Need([d isKindOfClass:NSDictionary.class]&&d.count==10&&[x isKindOfClass:NSDictionary.class],@"original synthetic stats dictionaries");
 NSMutableData*restored=[NSMutableData dataWithLength:0x2990];populate(restored.mutableBytes,d);populateExtended(restored.mutableBytes,x);
 Need([before isEqual:SHA75(stats.bytes,stats.length)],@"serializer mutated stats input");Need(memcmp((char*)stats.bytes+0x2800,(char*)restored.bytes+0x2800,360)==0,@"90 synthetic global float32 values failed original dictionary roundtrip");Need(memcmp((char*)stats.bytes+0x2970,(char*)restored.bytes+0x2970,8)==0,@"two extended float32 values failed original dictionary roundtrip");
 NSData*canonical=[NSJSONSerialization dataWithJSONObject:@{@"stats":d,@"xstats":x}options:NSJSONWritingSortedKeys error:NULL];Need(canonical!=nil,@"finite synthetic stats JSON");
 NSMutableDictionary*proof=[@{@"dictionary":d,@"extended_dictionary":x,@"global_field_vector_as_raw_f32_control":@[@.01f,@.03f,@.08f,@.15f,@.3f,@.45f,@.7f,@.9f,@1.f],@"SSRStats_bytes":@0x2990,@"SSRGlobalStats_offset":@0x2800,@"records":@10,@"floats_per_record":@9,@"extended_offset":@0x2970,@"original_C_bindings":bindings,@"input_stats_SHA_before":before,@"input_stats_SHA_after":SHA75(stats.bytes,stats.length),@"global90_and_extended2_f32_original_roundtrip_exact":@YES,@"canonical_dictionary_SHA256":SHA75(canonical.bytes,canonical.length),@"synthetic_not_actual_camera_statistics":@YES,@"field_names_not_used_as_physical_domain_evidence":@YES}mutableCopy];return proof;
}
