To reproduce our results, please download the TOP500lists directory and Python scripts from this repo.

1. To filter out Academic entries into two directories TOP500withoutAcademic/ TOP500Academic/ run the following command:

python3.6 filterAcademic.py TOP500lists/ 

2. To produce segment distribution stats, run:

python3.6 segment_distribution_stats.py TOP500lists/

Once the segment_distribution_stats.csv has been generated, we can go ahead and create Figure 1. Here we will have to run the plot_segment_distribution-lines.py script:

python3.6 plot_segment_distribution-lines.py analysis/segment_distribution_stats.csv

3. To produce rmax statistics for both Academic and non-Academic entries, run:

python3.6 performance_development-quantiles.py ../TOP500Academic/ -o rmax_statistics_academic.csv

python3.6 performance_development-quantiles.py ../TOP500withoutAcademic/ -o rmax_statistics_non_academic.csv


Once rmax_statistics_academic.csv and rmax_statistics_non_academic.csv have been generated, we can go ahead and create Figure 2. Here we will have to run the
plot_performance_development_comparison.py script:

python3.6 plot_performance_development_comparison.py analysis/rmax_statistics_academic.csv analysis/rmax_s
tatistics_non_academic.csv


For Figure 3, we have to run plot_performance_development-box-plot-normalized.py script:

python3.6 plot_performance_development-box-plot-normalized.py analysis/rmax_statistics_academic.csv
 
4. To create power statistics and generate power_statistics_academic.csv and power_statistics_non_academic.csv we need to run:

python3.6 power_statistics.py ../TOP500Academic/ -o power_statistics_academic.csv

python3.6 power_statistics.py ../TOP500Academic/ -o power_statistics_non_academic.csv

To plot figure 4, we need to run:
python3.6 plot_power_statistics_comparison_full.py analysis/power_statistics_academic.csv analysis/power_statistics_non_academic.csv

5. To generate energy efficiency stats for academic and non-academic entries, we need to run:

python3.6 energy_efficiency.py ../TOP500Academic/ -o energy_efficiency_quantiles_academic.csv

python3.6 energy_efficiency.py ../TOP500withoutAcademic/ -o energy_efficiency_quantiles_non_academic.csv

To plot Figure 5, we need to run:
python3.6 plot_energy_efficiency-box-plot_comparison_full.py analysis/energy_efficiency_quantiles_academic.csv analysis/energy_efficiency_quantiles_non_academic.csv

6.To look into system performance statistics, we run:
python3.6 system_performance_stats.py ../TOP500Academic/ -o system_performance_statistics.csv

Once the system_performance_statistics.csv is generated, we can plot Figure 6 by running:

python3.6 plot_system_performance_stat.py analysis/system_performance_statistics.csv

7. Creating accelerator statistics, we run:

python3.6 accelerators.py ../TOP500Academic/ -o accelerator_statistics.csv

Then to create Figure 7, we run:

python3.6 plot_accelerators.py
python3.6 plot_accelerators.py analysis/accelerator_statistics.csv

8. To generate architecture brand statistics for both academic and non-academic systems, we run:

python3.6 architecture_stats.py ../TOP500Academic/ -o architecture_brand_statistics_academic.csv

python3.6 architecture_stats.py ../TOP500withoutAcademic/ -o architecture_brand_statistics_non_academic.csv

Once these files are created, we can generate Figures 8 and 9:
python3.6 plot_architecure_brands.py analysis/architecture_brand_statistics_academic.csv

9. We also analyze age, and to do that we run: 
python3.6 analyze_age.py ../TOP500Academic/ -o age_statistics_academic.csv

python3.6 analyze_age.py ../TOP500withoutAcademic/ -o age_statistics_non_academic.csv

To plot Figure 10, run:
python3.6 plot_age.py

10. For interconnect stats, we run:
python3.6 interconnect_family.py ../TOP500Academic/

Once the csv is created, we modify it by hand to group 11 interconnect families into 4 groups.

Then, to plot Figure 10 we run:
python3.6 plot_interconnect_family.py analysis/interconnect_family_counts_201006_to_202606-modified.csv

11. To generate geographical stats, we run:
python3.6 geographic_distribution.py ../TOP500Academic/
