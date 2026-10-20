#import "../texture-producer-20261020/native_common.h"
#import "../texture-producer-20261020/matching.h"

int main(int argc,char **argv) {
    @autoreleasepool {
        if(argc!=2)return 64;
        NSArray *roles=@[@"instance-1",@"instance-2"];
        NSArray *edges=@[@{@"face_index":@0,@"instance_role":roles[0],@"face_probability_overlap":@0.90},
                         @{@"face_index":@0,@"instance_role":roles[1],@"face_probability_overlap":@0.89},
                         @{@"face_index":@1,@"instance_role":roles[0],@"face_probability_overlap":@0.88},
                         @{@"face_index":@1,@"instance_role":roles[1],@"face_probability_overlap":@0.01}];
        NSDictionary *matched=SelectFaceInstances(edges,roles,2);
        BOOL passed=matched.count==2 && [matched[@0][@"instance_role"] isEqual:roles[1]] && [matched[@1][@"instance_role"] isEqual:roles[0]];
        passed &= SelectFaceInstances(@[@{@"face_index":@0,@"instance_role":roles[0],@"face_probability_overlap":@0.001}],roles,1).count==0;
        passed &= SelectFaceInstances(@[],roles,0).count==0;
        Write(@{@"passed":@(passed),@"ambiguous_assignment":matched,@"scope":@"functional matching regression: greedy drops a match; low overlap and empty inputs stay unmatched"},@(argv[1]));
        return passed?0:1;
    }
}
