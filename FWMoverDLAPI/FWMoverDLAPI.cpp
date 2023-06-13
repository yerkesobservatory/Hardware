// FWMoverDLAPI.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include "include/dlapi.h"
#include <iostream>
#include <Windows.h> // for windows
// #include <unistd.h> // for linux
int main()
{
    dl::IGatewayPtr pGateway = dl::getGateway();
    // Query USB Cameras is a blocking call
    pGateway->queryUSBCameras();
    // Only proceed if a camera was found
    if (pGateway->getUSBCameraCount() <= 0) {
        return 1;
    }
    // Obtain the first USB camera found
    dl::ICameraPtr pCamera = pGateway->getUSBCamera(0);
    dl::deleteGateway(pGateway);
    // Initialize the camera (required to enable I/O)
    pCamera->initialize();
    // Create a buffer for the camera's serial string &amp; retrieve it.
    char buf[512] = { 0 };
    size_t lng = 512;
    pCamera->getSerial(&(buf[0]), lng);
    std::cout << std::string(&(buf[0]), lng) << std::endl;

    dl::IFWPtr pIFW = pCamera->getFW();
    dl::IPromisePtr pIFWPromise = pIFW->initialize();

    std::string line;
    int iLine;
    dl::IFW::Status status;

    while (true) {
        std::cout << "Enter a filter position: " << std::endl;
        std::cin >> line;
        if (line == "q") {
            std::cout << "Done" << std::endl;
            return 0;
        }
        iLine = std::atoi(line.c_str());
        if (iLine > 9 || iLine < 0) {
            std::cout << "Enter a valid filter position (0-9)" << std::endl;
        } else {
            do {
                pIFWPromise = pIFW->queryStatus();
                status = pIFW->getStatus();
            } while (status != dl::IFW::Status::FWIdle);
            pIFWPromise = pIFW->setPosition(iLine);
            do {
                pIFWPromise = pIFW->queryStatus();
                status = pIFW->getStatus();
                std::cout << ".";
                Sleep(1000);
            } while (status != dl::IFW::Status::FWIdle);
        }
        std::cout << line << std::endl;
    }

    return 0;
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
