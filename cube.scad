
module FilamentCalibrationCube()
{
	width = 20;
	heigh = 20;
	depth = 4;
    wallThickness = 1.2;
    topThickness = 1;

	difference() {
        cube([width, heigh, depth]);
        translate([wallThickness,wallThickness,0.3]) cube([width-2*wallThickness,heigh-2*wallThickness,depth-topThickness-0.3]);
    };
}

FilamentCalibrationCube();

