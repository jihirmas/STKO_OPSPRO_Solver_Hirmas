model basic -ndm 3 -ndf 3

set time_list [list \
__time__]
set strain_list [list \
__strain__]
timeSeries Path 1 -time $time_list -values $strain_list
timeSeries Linear 2

__materials__

set L __lch__
node 1  0  0  0
node 2 $L  0  0
node 3  0 $L  0
node 4  0  0 $L
element FourNodeTetrahedron 1   1 2 3 4   __tag__

fix 1   1 1 1
fix 2   0 1 1
fix 3   0 0 1

set flags1 [list __flags1__]
set flags2 [list __flags2__]
set imps   [list __imps__]

if {[lindex $flags1 0] == 1} { pattern Plain 1 2 -fact [expr $L*$L/6.0] { load 2 [lindex $imps 0] 0 0 } }
if {[lindex $flags1 1] == 1} { pattern Plain 2 2 -fact [expr $L*$L/6.0] { load 3 0 [lindex $imps 1] 0 } }
if {[lindex $flags1 2] == 1} { pattern Plain 3 2 -fact [expr $L*$L/6.0] { load 4 0 0 [lindex $imps 2] } }
if {[lindex $flags1 3] == 1} { pattern Plain 4 2 -fact [expr $L*$L/6.0] { load 3 [lindex $imps 3] 0 0 } }
if {[lindex $flags1 4] == 1} { pattern Plain 5 2 -fact [expr $L*$L/6.0] { load 4 0 [lindex $imps 4] 0 } }
if {[lindex $flags1 5] == 1} { pattern Plain 6 2 -fact [expr $L*$L/6.0] { load 4 [lindex $imps 5] 0 0 } }

if {[lindex $flags1 0] == 2} { if {[lindex $flags2 0] == 2} { pattern Plain 10 2 { sp 2 1 [expr $L*[lindex $imps 0]] } } }
if {[lindex $flags1 1] == 2} { if {[lindex $flags2 1] == 2} { pattern Plain 20 2 { sp 3 2 [expr $L*[lindex $imps 1]] } } }
if {[lindex $flags1 2] == 2} { if {[lindex $flags2 2] == 2} { pattern Plain 30 2 { sp 4 3 [expr $L*[lindex $imps 2]] } } }
if {[lindex $flags1 3] == 2} { if {[lindex $flags2 3] == 2} { pattern Plain 40 2 { sp 3 1 [expr $L*[lindex $imps 3]] } } }
if {[lindex $flags1 4] == 2} { if {[lindex $flags2 4] == 2} { pattern Plain 50 2 { sp 4 2 [expr $L*[lindex $imps 4]] } } }
if {[lindex $flags1 5] == 2} { if {[lindex $flags2 5] == 2} { pattern Plain 60 2 { sp 4 1 [expr $L*[lindex $imps 5]] } } }

constraints Transformation
numberer Plain
system UmfPack
test NormDispIncr 1.0e-6 1000 0
algorithm Newton
integrator LoadControl 0.1
analysis Static
set ok [analyze 10]
if {$ok != 0} {
	return
}
loadConst -time 0.0

wipeAnalysis

constraints Transformation
numberer Plain
system UmfPack
test NormDispIncr 1.0e-6 1000 0
algorithm Newton

if {[lindex $flags1 0] == 2} { if {[lindex $flags2 0] == 1} { pattern Plain 100 1 { sp 2 1 $L } } }
if {[lindex $flags1 1] == 2} { if {[lindex $flags2 1] == 1} { pattern Plain 200 1 { sp 3 2 $L } } }
if {[lindex $flags1 2] == 2} { if {[lindex $flags2 2] == 1} { pattern Plain 300 1 { sp 4 3 $L } } }
if {[lindex $flags1 3] == 2} { if {[lindex $flags2 3] == 1} { pattern Plain 400 1 { sp 3 1 $L } } }
if {[lindex $flags1 4] == 2} { if {[lindex $flags2 4] == 1} { pattern Plain 500 1 { sp 4 2 $L } } }
if {[lindex $flags1 5] == 2} { if {[lindex $flags2 5] == 1} { pattern Plain 600 1 { sp 4 1 $L } } }

set outFile [open "__out__" w+]
set num_step [llength $time_list]
set perc_incr [expr 1.0/$num_step]
set perc 0.0
set lambda_old 0.0
for {set i 0} {$i < $num_step} {incr i} {
	set perc [expr $perc + $perc_incr]
	set lambda [lindex $time_list $i]
	set d_lambda [expr $lambda - $lambda_old]
	set lambda_old $lambda
	integrator LoadControl $d_lambda
	analysis Static
	set ok [analyze 1]
	if {$ok != 0} {
		break
	}
	set strain [eleResponse 1 material 1 strain]
	set stress [eleResponse 1 material 1 stress]
	puts $outFile "$perc $strain $stress"
	puts "__R__$perc|$strain|$stress"
}
close $outFile
