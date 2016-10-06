$fn = 50;
module nema17(){


        cube([39, 42.3, 42.3], center = true);
        translate([19.5, 0, 0]){

            for(i=[0:4]){
                rotate([0,90, 0]){
                    translate([15.5, 15.5, 0]){
                        cylinder(20, d = 4, center = true);
                    }
                    translate([15.5, -15.5, 0]){
                        cylinder(20, d = 4, center = true);
                    }
                    translate([-15.5, 15.5, 0]){
                        cylinder(20, d = 4, center = true);
                    }
                    translate([-15.5, -15.5, 0]){
                        cylinder(20, d = 4, center = true);
                    }
                }
            }
        
    }
    
  
}
module shaft(){

    difference(){
        translate([32.5, 0, 0]){
            rotate([0, 90, 0]){
                translate([0, 0, -13]){
                    cylinder(2,d=22, center = true);
                }
                cylinder(26, d = 5, center = true);
            }
        }
    }
}
shaft();
nema17();