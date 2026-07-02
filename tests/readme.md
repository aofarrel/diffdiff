## what's in this test dataset?

Edge cases:
* Should 133 and 195 be highlighted as SNP-SNP incongruence instead of SNP-ref incongruence? --> currently not but may change later
* Should 150 be highlighted as SNP-SNP incongruence instead SNP-mask incongruence? --> No, because mask silences all SNPs
* Should 151 be highlighted as SNP-ref incongruence instead SNP-mask incongruence? --> No, because mask silences all SNPs


|     | x | y | z | justification                    |
|-----|---|---|---|----------------------------------|
| 123 | A | A | A | all SNP                          |
| 125 | G | - | R | one masks, one SNP, one ref      |
| 133 | T | R | C | ref+different SNPs               |
| 150 | A | - | T | mask different SNPs              |
| 151 | R | - | C | parse Y's long mask correctly    |
| 152 | A | R | R | end Y's long mask correctly      |
| 155 | R | R | A | end Y's long mask correctly      |
| 160 | - | - | - | all mask                         |
| 161 | - | - | - | all long mask                    |
| 162 | - | - | - | all long mask                    |
| 163 | - | - | - | all long mask                    |
| 164 | - | - | - | all long mask                    |
| 165 | - | - | - | y and z long mask, x ref         |
| 166 | R | - | - | y and z long mask, x ref         |
| 167 | R | - | - | y and z long mask, x ref         |
| 168 | R | - | - | y and z long mask, x ref         |
| 169 | R | - | - | y and z long mask, x ref         |
| 170 | T | - | - | y ans z long mask, x SNP         |
| 171 | R | - | - | y and z long mask, x ref         |
| 172 | R | - | - | y and z long mask, x ref         |
| 173 | R | - | R | y's long mask                    |
| 174 | R | - | R | y's long mask                    |
| 174 | R | - | R | y's long mask                    |
| 175 | G | G | C | highlighting SNP-SNP mismatch    |
| 179 | G | R | C | ref+different SNPs               |
| 179 | - | - | - | all mask                         |
| 180 | A | R | A |                                  |
| 181 | A | R | A |                                  |
| 182 | A | R | R |                                  |
| 195 | T | R | A |                                  |
| 196 | A | R | R |                                  |