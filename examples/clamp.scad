outer_dia = 22;
inner_dia = 16.25;
thickness = 10;
screw_dia = 3.5;

cylinder(d=outer_dia, h=thickness, center=true);
↑↑
union()
{↓←	⇲
translate([15,0,0]) cube([10,8,thickness], center=true);
}
↑↑↑↑↑↑
difference ()
{↓⇱⇓⇓⇓⇓⇓⇥→	cylinder(d=inner_dia, h=thickness+0.1, center=true);
}
↑↑⇲
translate([13,0,0]) cube([14+0.1, 2, thickness+0.1], center=true);
translate([15,0,0]) rotate([90,90,0]) cylinder(d=screw_dia, h=20, center=true);
