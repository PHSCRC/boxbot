module handle(){
    handlebase();
    handletop();
}
module handlebase(){
    difference(){
        union(){
//            translate([-120,0,-10]){
//                cube([10, 230, 10],center = true);
//            }
            translate([85,-0,0]){
                cube([50, 230, 15], center = true);
                handlebaseslide();
            }
        }
        handletop();
    
    }

}
module handletop(){

        union(){
            translate([-17.5,0,50]){
                cube([215, 60, 10],center = true);
            }
            translate([85,0,25]){
                cube([10,60,40],center = true);
            }
            translate([-120,0,25]){
                cube([10,60,60],center = true);
            }
            translate([85,-20,4]){
                cylinder(8, d = 8, center = true);
            }
            translate([85,20,4]){
                cylinder(8, d = 8, center = true);
            }   
            translate([-120, 20,-8]){
                cylinder(8, d = 8, center = true);
            }
            translate([-120, -20, -8]){
                cylinder(8, d = 8, center = true);
            }               
        }

}
module handlebaseslide(){
    difference(){
        translate([0, 0, -25]){
            rotate([90,90,0]){
                rotate([0,0,30]){
                    cylinder(230, d = 50, center = true, $fn = 6);
                }
            }
        }
        translate([0,0,-35]){
            cube([50,231, 35], center = true);
        }
    }
}
handle();