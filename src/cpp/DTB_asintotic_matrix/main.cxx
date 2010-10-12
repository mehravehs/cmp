#include <iostream>
#include <fstream>
#include <string>

#include <blitz/array.h>
#include <nifti1.h>

using namespace std;
using namespace blitz;

#include <boost/program_options.hpp>
namespace po = boost::program_options;

#include "lib_ui.cxx"
#include "lib_nii.cxx"
#include "lib_trk.cxx"


string 	BASE_filename, MASK_filename, BASE_outname, BASE_filename_2;
string	ROI_filename;
float	maxAngle, maxAngle_2;
int		CONFIG__seeds;

int 	CONFIG__minLength;
float 	CONFIG__stepSize;


Array<UINT8,4> CONNECTIONS;
Array<int,1> ROI_size(83);	// roi numbers are in 0..82 range (LABEL-1)
NII<INT16>* niiROI;
NII<INT16>* niiVOL;

Array<float,2>	fiber(3,1000);
short int		tot;

Array<float,3> matrix(83,83,3);



#include "cmx_matrix.cxx"
#include "tractography.cxx"



/******************************/
/*----------  MAIN  ----------*/
/******************************/
int main(int argc, char** argv)
{
	/***** PARSING of INPUT parameters (achieved with BOOST libraries) *****/
	po::variables_map vm;
    try {
    	po::arg = "ARG";
		po::options_description desc("Parameters syntax");
        desc.add_options()
        	("roi", 		po::value<string>(&ROI_filename), "Gray matter ROI path/filename (e.g. \"data/ROI_HR_th.nii\")")
            ("odf", 		po::value<string>(&BASE_filename), "DSI path/prefix (e.g. \"data/dsi_\")")
            ("angle", 		po::value<float>(&maxAngle)->default_value(45), "ANGLE threshold [degree]")
            ("odf2", 		po::value<string>(&BASE_filename_2)->default_value(""), "Auxiliary DSI path/prefix (optional)")
            ("angle2", 		po::value<float>(&maxAngle_2)->default_value(60), "Auxiliary ANGLE threshold (optional)\n")
            ("wm", 			po::value<string>(&MASK_filename), "WM path/filename (e.g. \"data/mask.nii\")")
            ("out", 		po::value<string>(&BASE_outname), "OUTPUT path/prefix (e.g. \"data/fibers\" with no '.trk' suffix)\n")
            ("rSeed", 		po::value<int>(&CONFIG__seeds)->default_value(4), "number of random seed points per voxel")
            ("minLength", 	po::value<int>(&CONFIG__minLength)->default_value(3), "minimum length of a fiber [steps]")
            ("stepSize", 	po::value<float>(&CONFIG__stepSize)->default_value(0.5), "step size [mm]")
            ("help", "Print this help message")
        ;
        po::store(po::command_line_parser(argc, argv).options(desc).run(), vm);
        po::notify(vm);

        if ( argc<2 || vm.count("help") )
        {
			cout <<"\n"<<COLOR(33,40,0)<< desc <<COLOR_reset<<"\n\n";
			return 1;
		}
    }
    catch(exception& e) {
        cerr <<COLOR(30,41,0)<<"[ERROR]"<<COLOR(31,40,0)<< " "<<e.what() <<COLOR_reset<<"\n\n";
        return 1;
    }
    catch(...) {
        COLOR_error("Exception of unknown type!\n\n");
    }


	/* Check INOUT PARAMETERS */
	if ( !vm.count("roi") )
	{
		COLOR_error("'roi' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("odf") )
	{
		COLOR_error("'odf' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("wm") )
	{
		COLOR_error("'wm' parameter not set.\n\n");
		return 1;
	}
	if ( !vm.count("out") )
	{
		COLOR_error("'out' parameter not set.\n\n");
		return 1;
	}


	/* PRINT a summary of parameters */
	stringstream sStr;
	COLOR_print("\nFiber-tracking PARAMETERS:\n", COLOR_yellow, COLOR_black, COLOR_bold);

	COLOR_print("\tODF prefix\t:\t"+BASE_filename+"\n", COLOR_yellow);

	sStr <<"\tAngle\t\t:\t"<< maxAngle <<"°\n";
	COLOR_print( sStr.str(), COLOR_yellow );

	if ( !BASE_filename_2.empty() )
	{
		COLOR_print("\tAUX ODF prefix\t:\t"+BASE_filename_2+"\n", COLOR_yellow);
		sStr.str(""); sStr <<"\tAngle\t\t:\t"<< maxAngle_2 <<"°\n";
		COLOR_print( sStr.str(), COLOR_yellow );
	}

	sStr.str(""); sStr <<"\t# seeds/voxel\t:\t"<< CONFIG__seeds <<"\n";
	COLOR_print( sStr.str(), COLOR_yellow );

	COLOR_print("\tWM\t\t:\t"+MASK_filename+"\n", COLOR_yellow);
	COLOR_print("\tOUT filename\t:\t"+BASE_outname+"__*.dat\n", COLOR_yellow);

	return main__tractography();
}