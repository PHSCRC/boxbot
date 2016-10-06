duse <nema17.scad>
use <liposlide.scad>
use <pislide.scad>
use <handle.scad>

module body(){
    difference(){
        cube([250, 230, 200], center = true);
        translate([0, 0, 15]){
            cube([220, 200, 180.01], center = true);
        }
        translate([113, 0, 20]){
            cube([25,175,165], center = true);
        }
        translate([-80, 95, -53.5]){
            rotate([0, 0, 90]){
                #nema17();
                #shaft();  
            }
        }
        translate([-80,-95,-53.5]){
            rotate([0, 0, -90]){
                #nema17();
                #shaft();  
            }
        }
        translate([0,0,107]){
            #handle();
        }
        translate([60,0,-90]){
            cylinder(20.1, d = 22.1, center = true);
            translate([0,0,-10]){
                #sphere(10);
            }
        }
    }

    difference(){
        translate([-100,0,15]){
            cube([20,100,170], center = true);
        }
        translate([-70, 0, -5]){
            #3sliposlide();
        }
        translate([-107, 0, 75]){
            #pilipo();
        }
        
    }
    difference(){
        translate([10, 90, 15]){
            cube([100, 20, 170], center = true);
        }
        translate([110, 120, 55]){
            #pislide();
        }

    }
}
module wheel(){
    rotate([90,90,0]){
        cylinder(8, d =60, center = true);
    }
}
module pilipo(){
    cube([12, 55, 60],center = true);
}
module boxbot(){
    body();


}
//translate([-80,130,-85]){
//    wheel();
//}
boxbot();