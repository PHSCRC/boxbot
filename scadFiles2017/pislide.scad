use <liposlide.scad>
module pislide(){
    translate([-100, 0, 0]){
        rotate([0, 0, 90]){
            slide(100);
        }
    }
    
    
}
pislide();