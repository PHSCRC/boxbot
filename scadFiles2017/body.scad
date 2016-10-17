use <nema17.scad>
use <liposlide.scad>
use <pislide.scad>
use <handle.scad>




module body(){
    difference(){
       cube([250, 230, 200], center = true);
        translate([0, 0, 15]){
            cube([220, 200, 185.01], center = true);
        }
        translate([113, 0, 20]){
            cube([25,175,165], center = true);
        }
        translate([20, 95, -56.3]){
            rotate([0, 0, 90]){
                #nema17();
                #shaft();  
            }
        }
        translate([20,-95,-56.3]){
            rotate([0, 0, -90]){
                #nema17();
                #shaft();  
            }
        }
        translate([0,0,107]){
            #handle();
        }
        translate([-60,0,-90]){
            cylinder(20.1, d = 22.1, center = true);
            translate([0,0,-6]){
                #ballcaster();
            }
        }
    }

    difference(){
        translate([-90,-50,7.5]){
            cube([40,100,185], center = true);
        }
        translate([-50, -50, -5]){
            #3sliposlide();
        }
        translate([-100, -50, 70.1]){
            #pilipo();
        }
        
    }
    translate([-10,50,-0]){
        rotate([0,0,90]){
            difference(){
        
                translate([5,80, 7.5]){
                    cube([100, 40, 185], center = true);
                }
                translate([105, 100, 50.1]){
                    #pislide();
                }
                translate([5, 90, 70.1]){
                    rotate([0,0,90]){
                        #pilipo();
                    }
                }
            
            }
        }
    }
}

module pilipo(){
    cube([12, 55, 60],center = true);
}
module boxbot(){
    body();


}
module ballcaster(){
    cylinder(15, d=22, center = true);
    translate([0,0,-6]){
        sphere(r=10);       
    }

    
}
boxbot();